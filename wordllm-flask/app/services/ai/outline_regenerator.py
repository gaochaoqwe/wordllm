"""
章节大纲重新生成相关服务
"""
import json
import logging
from flask import current_app

from app.models.document import Document
from app.services.ai.content_extractor import ContentExtractor
from app.services.ai.model_caller import ModelCaller
from app.services.ai.prompt_handler import PromptHandler

logger = logging.getLogger(__name__)

class OutlineRegenerator:
    """章节大纲重新生成器"""
    
    @staticmethod
    def regenerate_outline(client, model, template_id, input_file_path=None, 
                          requirement=None, regenerate_config=None):
        """基于已有章节重新生成大纲
        
        Args:
            client: OpenAI客户端
            model: 模型名称
            template_id: 模板ID
            input_file_path: 输入文件路径（可选）
            requirement: 用户对重新生成的特殊要求（可选）
            regenerate_config: 重新生成配置，可包含保留哪些章节等（可选）
            
        Returns:
            dict: 包含重新生成的章节大纲
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
            
            # 3. 构建特殊提示词
            # 包含用户的特定要求和保留部分章节的配置
            special_instructions = ""
            if requirement:
                special_instructions += f"\n用户特别要求: {requirement}\n"
            
            # 如果提供了重新生成配置，处理保留章节逻辑
            preserved_chapters = []
            if regenerate_config and 'preserved_chapters' in regenerate_config:
                preserved_chapters = regenerate_config['preserved_chapters']
                if preserved_chapters:
                    chapters_str = "\n".join([f"{ch.get('chapterNumber', '')}: {ch.get('title', '')}" 
                                            for ch in preserved_chapters])
                    special_instructions += f"\n请保留以下章节(不要修改这些章节的编号和标题):\n{chapters_str}\n"
            
            # 4. 使用PromptHandler构建提示词
            prompt = PromptHandler.build_outline_regenerate_prompt(
                template_content,
                input_content,
                special_instructions
            )
            
            # 5. 使用ModelCaller调用模型
            response = ModelCaller.call_model(client, model, prompt)
            
            # 6. 处理结果
            from app.services.ai.result_processor import ResultProcessor
            result = ResultProcessor.process_outline_result(response)
            
            # 7. 如果配置中指定了要保留的章节，则将它们合并到结果中
            if preserved_chapters:
                # 根据章节编号组织生成结果和保留章节的字典
                generated_chapters_dict = {
                    ch.get('chapterNumber', ''): ch 
                    for ch in result.get('chapters', [])
                }
                
                # 将保留的章节添加到字典中
                for chapter in preserved_chapters:
                    chapter_number = chapter.get('chapterNumber', '')
                    if chapter_number:
                        generated_chapters_dict[chapter_number] = chapter
                
                # 重新组织章节顺序
                sorted_chapters = []
                for number in sorted(generated_chapters_dict.keys(), 
                                    key=lambda x: [int(n) if n.isdigit() else n 
                                                for n in x.split('.')]):
                    sorted_chapters.append(generated_chapters_dict[number])
                
                # 更新结果
                result['chapters'] = sorted_chapters
            
            # 验证并修复大纲结构
            ResultProcessor.validate_and_fix_outline_structure(result.get('chapters', []))
            
            # 计算章节数
            total_chapters = ResultProcessor.count_total_sections(result.get('chapters', []))
            logger.info(f"成功重新生成大纲，包含 {total_chapters} 个章节")
            
            return result
            
        except Exception as e:
            logger.error(f"重新生成大纲失败: {str(e)}")
            raise
