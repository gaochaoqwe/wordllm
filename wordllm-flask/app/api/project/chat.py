import logging
from flask import request, jsonify
from datetime import datetime
from app.api.error import bad_request, internal_error

logger = logging.getLogger(__name__)

def document_chat():
    """
    与AI对话，获取文档编写相关的帮助
    请求体应包含:
    - chapter: 章节信息，包含chapterNumber和title
    - messages: 聊天历史消息列表
    - template_id: 模板ID
    - input_file: (可选) 输入文件
    """
    try:
        # 解析请求数据
        data = request.get_json()
        if not data:
            return bad_request('无效的请求数据')
        
        chapter = data.get('chapter')
        messages = data.get('messages', [])
        template_id = data.get('template_id')
        
        if not chapter:
            return bad_request('必须提供章节信息')
        
        if not template_id:
            return bad_request('必须提供模板ID')
        
        # 这里简化实现，模拟AI回复
        ai_response = {
            'role': 'assistant',
            'content': f"我理解您正在编辑'{chapter.get('title')}'章节。可以请问您具体需要什么帮助吗？我可以提供内容建议、结构优化或其他写作相关支持。"
        }
        
        # 如果消息列表不为空，生成更具体的回复
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if last_message.get('role') == 'user':
                ai_response['content'] = f"收到您的问题：{last_message.get('content', '')}。我会尽力为您提供帮助。"
        
        # 返回结果
        response = {
            'success': True,
            'data': {
                'response': ai_response
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"文档聊天请求失败: {str(e)}")
        return internal_error(f"处理聊天请求失败: {str(e)}")
