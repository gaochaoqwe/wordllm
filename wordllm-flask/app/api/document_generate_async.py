from flask import request, jsonify, current_app
from app.api import bp
from app.api.error import bad_request
from app.models.document import Document
from app.models.project import Project, Chapter
from app import db
import threading
import json
from datetime import datetime
from app.services.ai.document_generation import DocumentGenerator

def async_generate_chapters(template_id, project_id, chapters):
    from flask import current_app
    app = current_app._get_current_object()  # 获取真实 app 实例
    def worker():
        with app.app_context():
            for ch in chapters:
                chapter_number = ch['chapterNumber']
                title = ch['title']
                db_chapter = None
                try:
                    db_chapter = Chapter.query.filter_by(project_id=project_id, chapter_number=chapter_number).first()
                    if db_chapter:
                        db_chapter.status = 'generating'
                        db.session.commit()
                    # AI生成内容
                    outline_structure = json.dumps(chapters, ensure_ascii=False)
                    result = DocumentGenerator.generate_chapter_content(
                        app.config['OPENAI_CLIENT'],
                        app.config['OPENAI_MODEL_NAME'],
                        template_id,
                        chapter_number,
                        title,
                        outline_structure
                    )
                    content = result['content'] if isinstance(result, dict) else result
                    # 写入内容和状态
                    if db_chapter:
                        db_chapter.content = content
                        db_chapter.status = 'done'
                        db_chapter.updated_at = datetime.now()
                        db.session.commit()
                except Exception as e:
                    if db_chapter:
                        db_chapter.status = 'failed'
                        db_chapter.error_message = str(e)
                        db.session.commit()
    threading.Thread(target=worker, daemon=True).start()


@bp.route('/documents/start-generate-content', methods=['POST'])
def start_generate_content():
    data = request.get_json() or {}
    template_id = data.get('template_id')
    project_id = data.get('project_id')
    chapters = data.get('chapters', [])
    if not template_id or not project_id or not chapters:
        return bad_request('缺少参数')
    # 启动异步生成
    async_generate_chapters(template_id, project_id, chapters)
    return jsonify({'success': True, 'message': '已启动章节内容生成'})
