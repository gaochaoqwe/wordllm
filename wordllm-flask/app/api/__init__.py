from flask import Blueprint

bp = Blueprint('api', __name__)

# 导入路由以便注册到蓝图
from app.api import template, error, ai_outline, document_generate_async
from app.api.project import bp as project_bp

# 注册项目蓝图
bp.register_blueprint(project_bp)
