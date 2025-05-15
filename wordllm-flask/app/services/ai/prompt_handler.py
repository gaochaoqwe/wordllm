"""
负责构建提示词的模块
"""
import logging

logger = logging.getLogger(__name__)

class PromptHandler:
    """处理提示词构建的工具类"""
    
    @staticmethod
    def build_outline_prompt(template_content, input_content, custom_outline_prompt=None):
        """构建生成大纲的提示词，使用外部提示词模板
        
        Args:
            template_content: 模板内容
            input_content: 输入文件内容
            
        Returns:
            str: 构建的提示词
        """
        from app.prompts.outline_generation import (
            OUTLINE_GENERATION_PROMPT, 
            INPUT_CONTENT_SECTION,
            NO_INPUT_CONTENT_SECTION
        )
        
        # 构建主提示词结构
        from app.prompts.outline_generation import (
            OUTLINE_GENERATION_PROMPT,
            INPUT_CONTENT_SECTION,
            NO_INPUT_CONTENT_SECTION
        )
        # 根据是否提供了输入文件决定使用哪个内容部分
        if input_content:
            input_section = INPUT_CONTENT_SECTION.format(input_content=input_content)
        else:
            input_section = NO_INPUT_CONTENT_SECTION
        
        # 使用提示词模板并填充内容
        prompt = OUTLINE_GENERATION_PROMPT.format(
            template_content=template_content,
            input_content_section=input_section
        )
        
        # 如果有自定义outline_prompt，作为补充说明拼接到末尾
        if custom_outline_prompt:
            logger.info(f"附加自定义outline_prompt到主提示词末尾")
            prompt = f"{prompt}\n\n补充说明：\n{custom_outline_prompt}"
        
        # 日志打印完整prompt
        print("================================================================================")
        print("最终发送给模型的完整Prompt:")
        print(prompt)
        print("================================================================================")
            

        
        logger.info(f"构建了大纲生成提示词，长度: {len(prompt)}字符")
        
        return prompt
        
    @staticmethod
    def build_subchapter_prompt(template_content, existing_chapters, input_content):
        """构建生成子章节（第3级和第4级）的提示词
        
        Args:
            template_content: 模板内容
            existing_chapters: 现有章节JSON字符串
            input_content: 输入文件内容
            
        Returns:
            str: 构建的提示词
        """
        from app.prompts.subchapter_generation import SUBCHAPTER_GENERATION_PROMPT
        from app.prompts.outline_generation import (
            INPUT_CONTENT_SECTION,
            NO_INPUT_CONTENT_SECTION
        )
        
        # 根据是否提供了输入文件决定使用哪个内容部分
        if input_content:
            input_section = INPUT_CONTENT_SECTION.format(input_content=input_content)
        else:
            input_section = NO_INPUT_CONTENT_SECTION
        
        # 使用提示词模板并填充内容
        prompt = SUBCHAPTER_GENERATION_PROMPT.format(
            template_content=template_content,
            existing_chapters=existing_chapters,
            input_content_section=input_section
        )
        
        logger.info(f"构建了子章节生成提示词，长度: {len(prompt)}字符")
        
        return prompt
        
    @staticmethod
    def build_outline_regenerate_prompt(template_content, input_content, special_instructions=""):
        """构建重新生成大纲的提示词
        
        Args:
            template_content: 模板内容
            input_content: 输入文件内容
            special_instructions: 特殊指令和要求（可选）
            
        Returns:
            str: 构建的提示词
        """
        from app.prompts.outline_regeneration import (
            OUTLINE_REGENERATION_PROMPT,
            INPUT_CONTENT_SECTION,
            NO_INPUT_CONTENT_SECTION
        )
        
        # 根据是否提供了输入文件决定使用哪个内容部分
        if input_content:
            input_section = INPUT_CONTENT_SECTION.format(input_content=input_content)
        else:
            input_section = NO_INPUT_CONTENT_SECTION
        
        # 使用提示词模板并填充内容
        prompt = OUTLINE_REGENERATION_PROMPT.format(
            template_content=template_content,
            input_content_section=input_section,
            special_instructions=special_instructions
        )
        
        logger.info(f"构建了大纲重新生成提示词，长度: {len(prompt)}字符")
        
        return prompt
        
    @staticmethod
    def build_document_content_prompt(chapter_number, chapter_title, outline_structure, template_content, input_content):
        """构建生成文档章节内容的提示词
        
        Args:
            chapter_number: 章节编号
            chapter_title: 章节标题
            outline_structure: 完整文档大纲结构（JSON字符串）
            template_content: 模板内容
            input_content: 输入文件内容
            
        Returns:
            str: 构建的提示词
        """
        from app.prompts.document_generation import (
            DOCUMENT_CONTENT_GENERATION_PROMPT,
            INPUT_CONTENT_SECTION,
            NO_INPUT_CONTENT_SECTION
        )
        
        # 根据是否提供了输入文件决定使用哪个内容部分
        if input_content:
            input_section = INPUT_CONTENT_SECTION.format(input_content=input_content)
        else:
            input_section = NO_INPUT_CONTENT_SECTION
        
        # 使用提示词模板并填充内容
        prompt = DOCUMENT_CONTENT_GENERATION_PROMPT.format(
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            outline_structure=outline_structure,
            template_content=template_content,
            input_content_section=input_section
        )
        
        logger.info(f"构建了章节'{chapter_title}'内容生成提示词，长度: {len(prompt)}字符")
        
        return prompt
