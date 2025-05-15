"""AI服务主模块 - 导入自模块化的结构

此文件以前包含完整的AIService实现，现已重构到更模块化的结构中。
点击以下文件查看相关实现：
- app/services/ai/service.py - 主服务文件
- app/services/ai/content_extractor.py - 内容提取模块
- app/services/ai/prompt_handler.py - 提示词处理模块
- app/services/ai/model_caller.py - 模型调用模块
- app/services/ai/result_processor.py - 结果处理模块
"""

# 从新的模块化结构中导入所需的类和函数
from app.services.ai import AIService, get_ai_service

# 保持兼容性，只导出这两个类/函数
__all__ = ['AIService', 'get_ai_service']
