from flask import request, jsonify
from app.models.project import Project, Chapter
from app import db
from app.api.error import bad_request, not_found

# 章节相关接口

def get_project_chapters(project_id):
    project = Project.query.get(project_id)
    if not project:
        return not_found('项目不存在')
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
    chapter_dicts = [
        {'id': c.id, 'chapter_number': c.chapter_number, 'title': c.title, 'content': c.content, 'parent_id': c.parent_id, 'order_index': c.order_index} for c in chapters
    ]
    return jsonify({'success': True, 'data': chapter_dicts})


def save_project_chapters(project_id):
    data = request.get_json() or {}
    chapters = data.get('chapters', [])
    if not isinstance(chapters, list) or not chapters:
        return bad_request('必须提供章节列表')
    Chapter.query.filter_by(project_id=project_id).delete()
    db.session.commit()
    new_ids = []
    for idx, ch in enumerate(chapters):
        chapter = Chapter(
            project_id=project_id,
            chapter_number=ch.get('chapter_number') or ch.get('chapterNumber') or ch.get('id'),
            title=ch.get('title') or '未命名章节',
            content=ch.get('content', ''),
            parent_id=ch.get('parent_id') or ch.get('parentId'),
            order_index=ch.get('order_index', idx)
        )
        db.session.add(chapter)
        db.session.flush()
        new_ids.append(chapter.id)
    db.session.commit()
    return jsonify({'success': True, 'data': {'ids': new_ids}})


def update_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return not_found('章节不存在')
    data = request.get_json() or {}
    chapter.title = data.get('title', chapter.title)
    chapter.content = data.get('content', chapter.content)
    chapter.order_index = data.get('order_index', chapter.order_index)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': chapter.id}})


def get_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return not_found('章节不存在')
    return jsonify({'success': True, 'data': {
        'id': chapter.id,
        'chapter_number': chapter.chapter_number,
        'title': chapter.title,
        'content': chapter.content,
        'parent_id': chapter.parent_id,
        'order_index': chapter.order_index
    }})
