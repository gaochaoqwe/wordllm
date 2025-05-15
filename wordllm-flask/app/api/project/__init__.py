from flask import Blueprint
from .routes import create_project, get_project, get_projects
from .chapters import get_project_chapters, save_project_chapters, update_chapter, get_chapter
from .document import generate_document_content, update_document
from .chat import document_chat

bp = Blueprint('project', __name__)

# 项目相关路由
bp.add_url_rule('/projects', view_func=create_project, methods=['POST'])
bp.add_url_rule('/projects', view_func=get_projects, methods=['GET'])
bp.add_url_rule('/projects/<int:project_id>', view_func=get_project, methods=['GET'])

# 章节相关路由
bp.add_url_rule('/projects/<int:project_id>/chapters', view_func=get_project_chapters, methods=['GET'])
bp.add_url_rule('/projects/<int:project_id>/chapters', view_func=save_project_chapters, methods=['POST'])
bp.add_url_rule('/chapters/<int:chapter_id>', view_func=update_chapter, methods=['PUT'])
bp.add_url_rule('/chapters/<int:chapter_id>', view_func=get_chapter, methods=['GET'])

# 文档生成相关路由
bp.add_url_rule('/documents/generate-content', view_func=generate_document_content, methods=['POST'])
bp.add_url_rule('/documents/<int:doc_id>', view_func=update_document, methods=['PATCH'])

# AI文档聊天相关路由
bp.add_url_rule('/documents/chat', view_func=document_chat, methods=['POST'])
