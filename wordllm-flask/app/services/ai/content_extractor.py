"""
负责从各种来源提取内容的模块
"""
import os
import logging
import mammoth
from flask import current_app

logger = logging.getLogger(__name__)

class ContentExtractor:
    """负责从模板和输入文件中提取内容的工具类"""
    
    @staticmethod
    def extract_template_content(template):
        """从模板中提取内容
        
        Args:
            template: 模板对象
            
        Returns:
            str: 提取的内容
        """
        content = template.content or ""
        
        # 如果模板有关联文件，尝试提取文件内容
        if template.file_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'template', template.file_path)
            if not os.path.exists(file_path):
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], template.file_path)
            
            if os.path.exists(file_path):
                file_content = ContentExtractor.extract_file_content(file_path)
                if file_content:
                    content += "\n\n模板文件内容:\n" + file_content
        
        return content
    
    @staticmethod
    def extract_file_content(file_path):
        """根据文件类型提取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 提取的内容
        """
        if not file_path:
            logger.warning("文件路径为空")
            return ""
            
        # 详细记录文件信息
        logger.info(f"尝试提取文件内容: {file_path}")
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return ""
            
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"检测到的文件类型: '{file_ext}'")
        
        try:
            if file_ext in ['.docx', '.doc']:
                with open(file_path, 'rb') as f:
                    result = mammoth.convert_to_html(f)
                    content = mammoth.extract_raw_text(f).value
                    logger.info(f"成功提取Word文件内容, 字符数: {len(content)}")
                    return content
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"成功提取文本文件内容, 字符数: {len(content)}")
                    return content
            else:
                logger.warning(f"不支持的文件类型: '{file_ext}'") 
                return ""
        except Exception as e:
            logger.error(f"提取文件内容失败: {str(e)}")
            return ""
