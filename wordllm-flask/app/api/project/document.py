import os
import uuid
import json
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
from app.models.document import Document
from app import db  # 添加缺失的导入
from app.api.error import bad_request, not_found, internal_error
from app.services.ai_service import get_ai_service
from app.services.ai.document_generation import DocumentGenerator
from flask import Blueprint

bp = Blueprint('project_document', __name__)

logger = logging.getLogger(__name__)

@bp.route('/documents/<int:doc_id>', methods=['PATCH'])
def update_document(doc_id):
    """
    PATCH 更新文档的 outline_prompt 字段
    """
    logger.info(f"[DEBUG-PATCH] 收到文档更新请求: doc_id={doc_id}")
    doc = Document.query.get(doc_id)
    if not doc:
        logger.error(f"[DEBUG-PATCH] 文档不存在: doc_id={doc_id}")
        return not_found('文档不存在')
    
    # 记录更新前的文档状态
    logger.info(f"[DEBUG-PATCH] 更新前文档状态: id={doc.id}, title={doc.title}, outline_prompt={doc.outline_prompt}")
    
    data = request.get_json() or {}
    logger.info(f"[DEBUG-PATCH] 收到的请求数据: {data}")
    
    updated = False
    if 'outline_prompt' in data:
        logger.info(f"[DEBUG-PATCH] 更新outline_prompt: {doc.outline_prompt} -> {data['outline_prompt']}")
        doc.outline_prompt = data['outline_prompt']
        updated = True
    if 'title' in data:
        logger.info(f"[DEBUG-PATCH] 更新title: {doc.title} -> {data['title']}")
        doc.title = data['title']
        updated = True
    
    # 记录更新后、提交前的文档状态
    logger.info(f"[DEBUG-PATCH] 数据库提交前文档状态: id={doc.id}, title={doc.title}, outline_prompt={doc.outline_prompt}")
    
    if updated:
        doc.updated_at = datetime.now()
        try:
            db.session.commit()
            logger.info(f"[DEBUG-PATCH] 数据库提交成功")
        except Exception as e:
            logger.error(f"[DEBUG-PATCH] 数据库提交失败: {str(e)}")
            db.session.rollback()
            return internal_error(f"数据库更新失败: {str(e)}")
    else:
        logger.info(f"[DEBUG-PATCH] 没有实际更新，跳过提交")
    
    # 验证更改是否真正保存
    refreshed_doc = Document.query.get(doc_id)
    logger.info(f"[DEBUG-PATCH] 数据库提交后重新查询文档状态: id={refreshed_doc.id}, title={refreshed_doc.title}, outline_prompt={refreshed_doc.outline_prompt}")
    
    return jsonify(doc.to_dict())

def generate_document_content():
    """
    生成文档内容
    请求体应包含:
    - template_id: 模板ID
    - chapters: 章节列表，包含chapterNumber和title
    - chapter_number: (可选) 指定要生成内容的章节编号，不提供则生成所有章节
    - input_file: (可选) 输入文件
    - outline_prompt: (可选) 大纲生成提示词，如有则优先并覆盖数据库
    """
    try:
        print('[后端调试] generate_document_content 入口')
        # 检查必要的字段
        data = request.get_json()
        print("[后端调试] request.get_json() 结果:", data, type(data))
        # 如果不是JSON格式，继续检查是否是form格式
        if data is None:
            template_id = request.form.get('template_id')
            chapters_data = request.form.get('chapters')
            chapter_number = request.form.get('chapter_number')
            outline_prompt = request.form.get('outline_prompt')
            print('[后端调试] 使用 form 方式，template_id:', template_id, type(template_id))
            print('[后端调试] chapters_data:', chapters_data, type(chapters_data))
            print('[后端调试] chapter_number:', chapter_number, type(chapter_number))
            print('[后端调试] outline_prompt:', outline_prompt)
            if chapters_data:
                chapters = json.loads(chapters_data)
            else:
                print('[后端调试] 缺少 chapters_data')
                return bad_request('必须提供章节列表')
        else:
            template_id = data.get('template_id')
            chapters = data.get('chapters', [])
            chapter_number = data.get('chapter_number')
            project_id = data.get('project_id')
            outline_prompt = data.get('outline_prompt')
            print('[后端调试] 使用 json 方式，template_id:', template_id, type(template_id))
            print('[后端调试] chapters:', chapters, type(chapters))
            print('[后端调试] chapter_number:', chapter_number, type(chapter_number))
            print('[后端调试] project_id:', project_id, type(project_id))
            print('[后端调试] outline_prompt:', outline_prompt)
        if not template_id:
            print('[后端调试] template_id 缺失')
            return bad_request('必须提供模板ID')
        print(f"[后端调试] 解析得到 chapters: {chapters} 类型: {type(chapters)}")
        if not chapters or not isinstance(chapters, list):
            print('[后端调试] chapters 字段无效:', chapters, type(chapters))
            return bad_request('必须提供有效的章节列表')
        template = Document.query.get(template_id)
        if not template:
            print(f'[后端调试] 未找到ID为{template_id}的模板')
        # ====== 新增：如有 outline_prompt 字段，优先用并写入数据库 ======
        if outline_prompt is not None:
            if outline_prompt != template.outline_prompt:
                print(f'[后端调试] outline_prompt 发生变更，写入数据库')
                template.outline_prompt = outline_prompt
                template.updated_at = datetime.now()
                db.session.commit()
        # ========================================================
            return not_found(f'未找到ID为{template_id}的模板')
        # 处理上传的输入文件
        input_file_path = None
        if 'input_file' in request.files:
            input_file = request.files['input_file']
            if input_file.filename:
                # 保存上传的文件
                original_filename = input_file.filename
                logger.info(f"原始文件名: {original_filename}")
                filename = secure_filename(original_filename)
                logger.info(f"secure_filename后的文件名: {filename}")
                # 为避免文件名冲突，添加时间戳
                file_ext = os.path.splitext(filename)[1]
                logger.info(f"提取的文件扩展名: '{file_ext}'")
                # 修正: 如果没有扩展名，尝试从content-type推断
                if not file_ext:
                    content_type = input_file.content_type
                    logger.info(f"文件的Content-Type: {content_type}")
                    # 根据MIME类型推断扩展名
                    if content_type == 'application/msword' or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        file_ext = '.docx'
                        logger.info("从content-type推断出扩展名.docx")
                    elif content_type == 'text/plain':
                        file_ext = '.txt'
                        logger.info("从content-type推断出扩展名.txt")
                    elif content_type == 'application/pdf':
                        file_ext = '.pdf'
                        logger.info("从content-type推断出扩展名.pdf")
                    else:
                        logger.warning(f"未知的content-type: {content_type}，使用.docx作为默认扩展名")
                        file_ext = '.docx'  # 默认使用.docx
                unique_filename = f"input_{uuid.uuid4().hex}{file_ext}"
                logger.info(f"生成的唯一文件名: {unique_filename}")
                # 确保目录存在
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'inputs')
                os.makedirs(upload_folder, exist_ok=True)
                input_file_path = os.path.join(upload_folder, unique_filename)
                input_file.save(input_file_path)
                logger.info(f"已保存输入文件: {input_file_path}")
        # 获取AI服务
        ai_service = get_ai_service()
        # 根据是否提供了指定章节，选择生成单个章节还是所有章节
        if chapter_number:
            # 查找指定章节
            chapter = next((ch for ch in chapters if ch['chapterNumber'] == chapter_number), None)
            if not chapter:
                return not_found(f'未找到编号为{chapter_number}的章节')
            # 检查请求中是否提供了project_id
            project_id = data.get('project_id')
            if not project_id:
                print("[ERROR] 缺少 project_id 参数")
                return bad_request('必须提供 project_id 参数才能生成章节内容')
            # 调用DocumentGenerator生成章节内容
            outline_structure = json.dumps(chapters, ensure_ascii=False)
            content = DocumentGenerator.generate_chapter_content(
                ai_service.client,
                ai_service.model,
                template_id,
                chapter['chapterNumber'],
                chapter['title'],
                outline_structure,
                input_file_path
            )
            # === 写入数据库 ===
            from app.models.project import Chapter as ChapterModel
            # 确保有project_id
            print(f"[DEBUG] 使用 project_id: {project_id} 更新数据库")
            db_chapter = ChapterModel.query.filter_by(project_id=project_id, chapter_number=chapter['chapterNumber']).first()
            if db_chapter:
                # 确保content是字符串，而不是字典
                if isinstance(content, dict) and 'content' in content:
                    print(f"[DEBUG] 内容是字典类型，提取content字段值")
                    db_chapter.content = content['content']
                else:
                    print(f"[DEBUG] 内容是字符串类型，直接保存")
                    db_chapter.content = str(content)
                db.session.commit()
            # === 新增：从数据库读取最新章节内容返回 ===
            db_chapter = ChapterModel.query.filter_by(project_id=project_id, chapter_number=chapter['chapterNumber']).first()
            response = {
                'success': True,
                'data': {
                    'chapter': {
                        'id': db_chapter.id,
                        'chapter_number': db_chapter.chapter_number,
                        'title': db_chapter.title,
                        'content': db_chapter.content,
                        'parent_id': db_chapter.parent_id,
                        'order_index': db_chapter.order_index
                    } if db_chapter else chapter,
                    'content': db_chapter.content if db_chapter else content
                },
                'timestamp': datetime.now().isoformat()
            }
        else:
            # 生成所有章节内容
            contents = DocumentGenerator.generate_document_content(
                ai_service.client,
                ai_service.model,
                template_id,
                chapters,
                input_file_path
            )
            # === 新增：写入数据库 ===
            from app.models.project import Chapter as ChapterModel
            # contents: { chapterNumber: content }
            # 先批量更新数据库
            project_id = None
            for ch in chapters:
                if 'project_id' in ch:
                    project_id = ch['project_id']
                    break
            if not project_id:
                # 可选：从其它上下文推断
                pass
            if project_id:
                for ch in chapters:
                    chapter_number = ch['chapterNumber']
                    content = contents.get(chapter_number)
                    db_chapter = ChapterModel.query.filter_by(project_id=project_id, chapter_number=chapter_number).first()
                    if db_chapter and content:
                        # 确保content是字符串，而不是字典
                        if isinstance(content, dict) and 'content' in content:
                            print(f"[DEBUG] 章节{chapter_number}内容是字典类型，提取content字段值")
                            db_chapter.content = content['content']
                        else:
                            print(f"[DEBUG] 章节{chapter_number}内容是字符串类型，直接保存")
                            db_chapter.content = str(content)
                db.session.commit()
                # 从数据库读取所有章节内容
                db_chapters = ChapterModel.query.filter_by(project_id=project_id).order_by(ChapterModel.order_index).all()
                result_chapters = [
                    {
                        'id': c.id,
                        'chapter_number': c.chapter_number,
                        'title': c.title,
                        'content': c.content,
                        'parent_id': c.parent_id,
                        'order_index': c.order_index
                    }
                    for c in db_chapters
                ]
            else:
                result_chapters = chapters
            response = {
                'success': True,
                'data': {
                    'chapters': result_chapters,
                    'generated_chapters': len(contents)
                },
                'timestamp': datetime.now().isoformat()
            }
        # 打印返回给前端的数据
        print("\n" + "=" * 80)
        print("返回给前端的数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        print("=" * 80 + "\n")
        return jsonify(response)
    except Exception as e:
        logger.exception('生成文档内容时发生异常')
        return internal_error(str(e))
