"""
文档导出API路由模块
提供导出文档为各种格式的API端点
"""
import os
import logging
from flask import request, send_file, jsonify, Blueprint
from app.api.error import bad_request, not_found, internal_error
from app.models.project import Project, Chapter
from app.services.document_export import DocumentExportService

bp = Blueprint('project_export', __name__)
logger = logging.getLogger(__name__)

@bp.route('/projects/<int:project_id>/export', methods=['POST'])
def export_document(project_id):
    """
    导出文档为 DOCX/PDF/TXT 格式
    请求体应包含：
    - format: 导出格式，可以是 'docx', 'pdf', 'txt'
    - settings: 格式设置（页边距、字体等）
    - scope: 导出范围，可以是 'all' 或 'current'
    - current_chapter: 如果 scope 是 'current'，则指定当前章节
    """
    try:
        logger.info(f"收到导出文档请求: project_id={project_id}")
        data = request.get_json()
        if not data:
            logger.error("未收到有效的JSON数据")
            return bad_request('无效的请求数据')
            
        # 获取导出设置
        export_format = data.get('format', 'docx')
        settings = data.get('settings', {})
        scope = data.get('scope', 'all')
        current_chapter = data.get('current_chapter')
        
        logger.info(f"导出格式: {export_format}, 范围: {scope}")
        logger.debug(f"设置: {settings}")
        
        # 获取项目信息
        project = Project.query.get(project_id)
        if not project:
            logger.error(f"项目不存在: {project_id}")
            return not_found('项目不存在')
            
        # 根据范围获取章节
        if scope == 'current' and current_chapter is not None:
            logger.info(f"仅导出当前章节: {current_chapter}")
            chapters = Chapter.query.filter_by(
                project_id=project_id, 
                chapter_number=current_chapter
            ).all()
        else:
            logger.info("导出所有章节")
            chapters = Chapter.query.filter_by(
                project_id=project_id
            ).order_by(Chapter.order_index).all()
            
        if not chapters:
            logger.error("没有找到章节内容")
            return bad_request('没有找到章节内容')
        
        logger.info(f"找到 {len(chapters)} 个章节")
            
        # 生成文档
        try:
            if export_format == 'docx':
                file_path = DocumentExportService.export_as_docx(project, chapters, settings)
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                ext = '.docx'
            elif export_format == 'pdf':
                # 先导出为DOCX，然后尝试转换为PDF
                docx_path = DocumentExportService.export_as_docx(project, chapters, settings)
                file_path = DocumentExportService.convert_to_pdf(docx_path)
                mime_type = 'application/pdf'
                ext = '.pdf'
            elif export_format == 'txt':
                file_path = DocumentExportService.export_as_txt(project, chapters, settings)
                mime_type = 'text/plain'
                ext = '.txt'
            else:
                logger.error(f"不支持的导出格式: {export_format}")
                return bad_request('不支持的导出格式')
        except Exception as e:
            logger.exception(f"导出文档时发生错误: {str(e)}")
            return internal_error(f"导出文档时发生错误: {str(e)}")
            
        # 构建文件名
        file_name = f"{getattr(project, 'project_name', None) or getattr(project, 'name', None) or f'project_{project_id}'}{ext}"
        
        # 发送文件
        logger.info(f"发送文件: {file_path}, 名称: {file_name}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype=mime_type
        )
            
    except Exception as e:
        logger.exception(f"处理导出请求时发生异常: {str(e)}")
        return internal_error(str(e))
