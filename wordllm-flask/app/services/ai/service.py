"""
AI服务主模块
"""
import json
import logging
import openai
from flask import current_app

from app.models.document import Document
from app.services.ai.content_extractor import ContentExtractor
from app.services.ai.model_caller import ModelCaller
from app.services.ai.prompt_handler import PromptHandler
from app.services.ai.result_processor import ResultProcessor

logger = logging.getLogger(__name__)

class AIService:
    """AI服务，处理OpenAI API调用相关功能"""
    
    def __init__(self):
        """初始化AI服务，配置OpenAI客户端"""
        try:
            # 获取必要的配置
            api_key = current_app.config.get('OPENAI_API_KEY')
            base_url = current_app.config.get('OPENAI_API_BASE')
            
            # 初始化OpenAI客户端
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # 设置模型名称
            self.model = current_app.config.get('OPENAI_MODEL_NAME', "gpt-3.5-turbo")
            
            logger.info(f"初始化OpenAI客户端成功，使用模型: {self.model}")
            
        except Exception as e:
            logger.error(f"初始化OpenAI客户端失败: {str(e)}")
            raise
    
    def generate_document_outline(self, template_id, input_file_path=None, custom_outline_prompt=None):
        """基于模板和输入文件生成文档大纲
        
        Args:
            template_id: 模板ID
            input_file_path: 输入文件路径 (可选)
            
        Returns:
            dict: 包含生成的章节大纲
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
            prompt = PromptHandler.build_outline_prompt(template_content, input_content, custom_outline_prompt)
            print(f"[测试-后端] 使用的提示词类型: {'自定义' if custom_outline_prompt else '默认'}")
            if custom_outline_prompt:
                print(f"[测试-后端] 自定义提示词: {custom_outline_prompt}")
            
            # 打印完整的提示词
            print("================================================================================")
            print("原始请求数据：")
            print(prompt)
            print("================================================================================")
            
            # 4. 使用ModelCaller调用模型
            response = ModelCaller.call_model(self.client, self.model, prompt)
            
            # 5. 使用ResultProcessor处理结果
            generated_outline = ResultProcessor.process_outline_result(response)
            
            # 6. 验证和修复大纲结构
            ResultProcessor.validate_and_fix_outline_structure(generated_outline.get('chapters', []))
            
            # 计算总章节数
            total_sections = ResultProcessor.count_total_sections(generated_outline.get('chapters', []))
            logger.info(f"成功生成大纲，包含 {len(generated_outline.get('chapters', []))} 个一级章节，共 {total_sections} 个章节")
            
            return generated_outline
            
        except Exception as e:
            logger.error(f"生成文档大纲失败: {str(e)}")
            raise
    
    def regenerate_document_outline(self, template_id, input_file_path=None, requirement=None, regenerate_config=None):
        """重新生成文档大纲
        
        Args:
            template_id: 模板ID
            input_file_path: 输入文件路径（可选）
            requirement: 用户对重新生成的特殊要求（可选）
            regenerate_config: 重新生成配置，可包含保留哪些章节等（可选）
            
        Returns:
            dict: 包含重新生成的章节大纲
        """
        from app.services.ai.outline_regenerator import OutlineRegenerator
        
        try:
            # 调用OutlineRegenerator服务
            result = OutlineRegenerator.regenerate_outline(
                self.client,
                self.model,
                template_id,
                input_file_path,
                requirement,
                regenerate_config
            )
            
            return result
        except Exception as e:
            logger.error(f"重新生成文档大纲失败: {str(e)}")
            raise
    
    def generate_subchapters(self, template_id, existing_chapters, input_file_path=None):
        """基于现有章节、模板和输入文件生成第3级和第4级子章节
        
        Args:
            template_id: 模板ID
            existing_chapters: 现有的章节列表，包含chapterNumber和title
            input_file_path: 输入文件路径 (可选)
            
        Returns:
            dict: 包含生成的子章节大纲
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
            
            # 3. 准备现有章节列表
            existing_chapters_json = json.dumps(existing_chapters, ensure_ascii=False, indent=2)
            
            # 4. 使用PromptHandler构建提示词
            prompt = PromptHandler.build_subchapter_prompt(template_content, existing_chapters_json, input_content)
            
            # 5. 使用ModelCaller调用模型
            response = ModelCaller.call_model(self.client, self.model, prompt)
            
            # 6. 使用ResultProcessor处理结果
            generated_subchapters = ResultProcessor.process_outline_result(response)
            
            # 7. 验证和修复子章节结构
            ResultProcessor.validate_and_fix_outline_structure(generated_subchapters.get('chapters', []))
            
            # 计算子章节数
            total_subchapters = ResultProcessor.count_total_sections(generated_subchapters.get('chapters', []))
            logger.info(f"成功生成子章节，包含 {total_subchapters} 个子章节")
            
            return generated_subchapters
            
        except Exception as e:
            logger.error(f"生成子章节大纲失败: {str(e)}")
            raise

# 实例缓存
_ai_service_instance = None

# 使用工厂函数代替直接实例化
def get_ai_service():
    """获取AI服务实例，确保在应用上下文中创建"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
