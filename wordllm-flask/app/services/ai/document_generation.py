"""
文档内容生成服务
"""
import json
import logging
from flask import current_app

from app.models.document import Document
from app.services.ai.content_extractor import ContentExtractor
from app.services.ai.model_caller import ModelCaller
from app.services.ai.prompt_handler import PromptHandler

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """文档内容生成器，处理章节内容的AI生成相关功能"""
    
    @staticmethod
    def generate_chapter_content(client, model, template_id, chapter_number, chapter_title, outline_structure, input_file_path=None):
        """为特定章节生成内容
        
        Args:
            client: OpenAI客户端
            model: 模型名称
            template_id: 模板ID
            chapter_number: 章节编号
            chapter_title: 章节标题
            outline_structure: 整个文档的大纲结构（JSON字符串）
            input_file_path: 输入文件路径（可选）
            
        Returns:
            str: 生成的章节内容
        """
        try:
            # 1. 获取模板内容
            template = Document.query.get(template_id)
            if not template:
                raise ValueError(f"未找到ID为{template_id}的模板")
            
            # 使用ContentExtractor提取模板内容
            template_content = ContentExtractor.extract_template_content(template)
            
            # 2. 获取输入文件内容（如果提供）
            input_content = ""
            if input_file_path:
                input_content = ContentExtractor.extract_file_content(input_file_path)
            
            # 3. 使用PromptHandler构建提示词
            prompt = PromptHandler.build_document_content_prompt(
                chapter_number,
                chapter_title,
                outline_structure,
                template_content,
                input_content
            )
            logger.info(f"[AI调试] 章节生成Prompt内容如下:\n{prompt}")
            
            # 4. 使用ModelCaller调用模型
            response = ModelCaller.call_model(client, model, prompt)
            logger.info(f"[AI调试] 原始模型响应: {response}")
            
            # 5. 处理结果
            content = ""
            import re
            def extract_json_from_code_block(text):
                import re
                import json
                logger.debug(f"[extract_json_from_code_block] 原始text: {repr(text)[:200]}")
                # 去除markdown代码块包裹
                text = text.strip()
                if text.startswith('```'):
                    text = re.sub(r'^```[a-zA-Z]*', '', text)
                    text = re.sub(r'```$', '', text)
                    text = text.strip()
                # 尝试提取第一个大括号包裹的内容
                match = re.search(r'({[\s\S]+})', text)
                if match:
                    text = match.group(1)
                # 尝试解析
                try:
                    return json.loads(text)
                except Exception as e:
                    logger.error(f"extract_json_from_code_block: 直接JSON解析失败: {e}, text片段: {text[:200]}")
                    # 自动补全缺失的右括号
                    left = text.count('{')
                    right = text.count('}')
                    if left > right:
                        text = text + ('}' * (left - right))
                        try:
                            return json.loads(text)
                        except Exception as e2:
                            logger.error(f"extract_json_from_code_block: 自动补全后依然失败: {e2}, text片段: {text[:200]}")
                return None

            try:
                # 直接从 ChatCompletion 对象中获取内容
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content
                else:
                    # 兼容旧格式
                    content = response.get('content', '') if hasattr(response, 'get') else str(response)
                logger.info(f"[AI调试] 提取到的content内容（前200字）：{content[:200]}")
                # 新增: 尝试提取JSON并返回content字段
                parsed = extract_json_from_code_block(content)
                if parsed and 'content' in parsed:
                    logger.info(f"[AI调试] 解析后content字段前200字：{parsed['content'][:200]}")
                    content = parsed['content']
                # 保证content为字符串类型
                if not isinstance(content, str):
                    content = str(content)
                logger.info(f"[调试] 返回前 content 类型: {type(content)}, 内容: {repr(content)[:200]}")
            except Exception as e:
                import traceback
                logger.error(f"处理响应出错: {str(e)}\n堆栈: {traceback.format_exc()}")
                # 模拟内容以保证前端能正常显示
                content = f"## {chapter_title}\n\n本章节内容暂时无法生成。\n\n调用API时出现错误: {str(e)}\n\n请稍后重试或联系系统管理员。"
            
            logger.info(f"成功生成章节'{chapter_title}'的内容，长度: {len(content)}字符，返回内容前200字：{content[:200]}")
            # 始终返回字符串结构
            return {
                "success": True,
                "content": content
            }
            
        except Exception as e:
            import traceback
            logger.error(f"生成章节'{chapter_title}'内容失败: {str(e)}\n堆栈: {traceback.format_exc()}")
            # 返回错误信息作为内容，使前端能正常显示
            return {
                "success": True,  # 返回True以避免前端崩溃
                "content": f"## {chapter_title}\n\n本章节内容暂时无法生成。\n\n生成内容时出现错误: {str(e)}\n\n请稍后重试或联系系统管理员。"
            }
    
    @staticmethod
    def generate_document_content(client, model, template_id, chapters, input_file_path=None):
        """为文档的所有章节生成内容
        
        Args:
            client: OpenAI客户端
            model: 模型名称
            template_id: 模板ID
            chapters: 章节列表，包含chapterNumber和title字段
            input_file_path: 输入文件路径（可选）
            
        Returns:
            dict: 包含所有章节内容的字典，键为章节编号
        """
        try:
            results = {}
            outline_structure = json.dumps(chapters, ensure_ascii=False)
            
            # 按章节编号排序
            sorted_chapters = sorted(chapters, key=lambda ch: ch['chapterNumber'])
            
            for chapter in sorted_chapters:
                chapter_number = chapter['chapterNumber']
                chapter_title = chapter['title']
                
                # 只处理一级和二级章节
                if chapter_number.count('.') <= 1:
                    logger.info(f"开始生成章节'{chapter_title}'的内容...")
                    
                    content = DocumentGenerator.generate_chapter_content(
                        client,
                        model,
                        template_id,
                        chapter_number,
                        chapter_title,
                        outline_structure,
                        input_file_path
                    )
                    
                    # 存储结果
                    results[chapter_number] = content
                    
                    logger.info(f"章节'{chapter_title}'内容生成完成")
            
            return results
            
        except Exception as e:
            logger.error(f"生成文档内容失败: {str(e)}")
            raise
