from flask import request, jsonify, current_app, Response, stream_with_context
import os
import uuid
import json
from datetime import datetime
from app.api import bp
from app.api.error import bad_request, not_found, internal_error
from app.models.document import Document
from app import db
from app.services.ai_service import get_ai_service
from app.services.ai.model_caller import ModelCaller
from app.services.ai.prompt_handler import PromptHandler
from app.services.ai.content_extractor import ContentExtractor
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

@bp.route('/outlines/generate-streaming', methods=['POST'])
def generate_outline_streaming():
    """
    流式生成标书大纲
    请求体应包含:
    - template_id: 模板ID
    - input_file: (可选) 输入文件
    """
    try:
        # 检查模板ID
        template_id = request.form.get('template_id')
        if not template_id:
            return bad_request('必须提供template_id参数')
        
        template = Document.query.get(template_id)
        if not template:
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
        
        # 检查是否有自定义提示词
        outline_prompt = request.form.get('outline_prompt')
        print(f"[测试-后端] 接收到的outline_prompt: {outline_prompt}")
        
        # 获取项目ID
        project_id = request.form.get('project_id')
        if not project_id:
            return bad_request('必须提供project_id参数')
            
        # 准备AI服务调用所需的数据
        # 1. 获取模板内容
        template_content = ContentExtractor.extract_template_content(template)
        
        # 2. 获取输入文件内容（如果提供）
        input_content = ""
        if input_file_path:
            input_content = ContentExtractor.extract_file_content(input_file_path)
        
        # 3. 使用PromptHandler构建提示词
        prompt = PromptHandler.build_outline_prompt(template_content, input_content, outline_prompt)
        print(f"[测试-后端] 使用的提示词类型: {'自定义' if outline_prompt else '默认'}")
        
        # 4. 获取AI客户端
        ai_service = get_ai_service()
        
        def generate():
            """流式生成响应内容"""
            try:
                # 使用流式响应调用模型
                # 注意：使用ai_service实例已初始化的client
                # 如果在ModelCaller中无法获取到client，它会自动从配置文件创建新的客户端
                # 传送ai_service.client而不是None
                response_stream = ModelCaller.call_model_streaming(ai_service.client, ai_service.model, prompt)
                
                # 发送响应头部，告诉前端这是JSON类型
                yield '{"success":true,"streaming":true,"content":"'
                
                # 保存完整的响应内容，用于后续解析和存储
                full_content = ""
                
                # 新版OpenAI SDK (1.0.0+)的流式响应格式
                for chunk in response_stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        if content:
                            # 对特殊字符进行转义，确保JSON有效
                            escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            full_content += content
                            # 实时返回内容
                            yield escaped_content
            except Exception as e:
                logger.error(f"流式调用错误: {str(e)}")
                logger.exception(e)  # 输出完整堆栈跟踪
                yield f'\\n\\n错误: {str(e)}"}}'
                return  # 值退出生成器
            
            # 尝试解析全部内容为JSON
            try:
                from sqlalchemy import and_
                from app.models.project import Chapter
                from app import db
                
                # 尝试解析JSON内容
                # 清理可能的非JSON前缀
                processed_content = full_content
                if '```json' in processed_content:
                    processed_content = processed_content.split('```json')[1]
                if '```' in processed_content:
                    processed_content = processed_content.split('```')[0]
                
                # 查找JSON开始和结束的位置
                start_idx = processed_content.find('{')
                end_idx = processed_content.rfind('}')
                if start_idx >= 0 and end_idx > start_idx:
                    processed_content = processed_content[start_idx:end_idx+1]
                
                # 解析为JSON对象
                outline_result = json.loads(processed_content)
                
                # 设置chapters如果不存在
                if 'chapters' not in outline_result:
                    if isinstance(outline_result, list):
                        outline_result = {"chapters": outline_result}
                    else:
                        outline_result = {"chapters": []}
                
                # 先删除该项目下所有章节
                Chapter.query.filter_by(project_id=project_id).delete()
                db.session.commit()
                
                # 保存章节到数据库
                ai_chapters = outline_result.get('chapters', [])
                for idx, ch in enumerate(ai_chapters):
                    chapter_number = ch.get('chapterNumber') or ch.get('chapter_number') or ch.get('id')
                    title = ch.get('title') or '未命名章节'
                    content = ch.get('content', '')
                    parent_id = ch.get('parent_id') or ch.get('parentId')
                    
                    db_chapter = Chapter(
                        project_id=project_id,
                        chapter_number=chapter_number,
                        title=title,
                        content=content,
                        parent_id=parent_id,
                        order_index=idx
                    )
                    db.session.add(db_chapter)
                db.session.commit()
                
                # 正常结束响应
                yield '","parsed":true,"template":{"id":' + str(template.id) + ',"title":"' + template.title + '"},"timestamp":"' + datetime.now().isoformat() + '"}'
            
            except Exception as e:
                logger.error(f"解析或保存章节失败: {str(e)}")
                # 结束响应，但标记解析失败
                yield '","parsed":false,"error":"' + str(e) + '"}'
        
        # 返回流式响应
        return Response(stream_with_context(generate()), content_type='application/json')
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"流式生成大纲失败: {str(e)}")
        logger.error(f"错误详情:\n{error_trace}")
        return jsonify({
            'success': False,
            'message': f"生成大纲失败: {str(e)}"
        }), 500

@bp.route('/outlines/generate', methods=['POST'])
def generate_outline():
    """
    生成标书大纲
    请求体应包含:
    - template_id: 模板ID
    - input_file: (可选) 输入文件
    """
    try:
        # 检查模板ID
        template_id = request.form.get('template_id')
        if not template_id:
            return bad_request('必须提供template_id参数')
        
        template = Document.query.get(template_id)
        if not template:
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
        
        # 检查是否有自定义提示词
        outline_prompt = request.form.get('outline_prompt')
        print(f"[测试-后端] 接收到的outline_prompt: {outline_prompt}")
        
        # 调用AI服务生成大纲
        ai_service = get_ai_service()
        outline_result = ai_service.generate_document_outline(template_id, input_file_path, outline_prompt)
        
        # === 新增：将AI生成的大纲直接存入数据库 ===
        from app.models.project import Chapter
        # 先删除该项目下所有章节
        project_id = request.form.get('project_id')
        if not project_id:
            return bad_request('必须提供project_id参数')
        Chapter.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        # === 新逻辑：只处理3/4级章节 ===
        def is_3_or_4_level(chap_num):
            return chap_num and str(chap_num).count('.') >= 2
        chapters = outline_result.get('chapters', [])
        ai_chapters = chapters  # 不做过滤，全部写入
        ai_numbers = set((ch.get('chapterNumber') or ch.get('chapter_number') or ch.get('id')) for ch in ai_chapters)
        # 删除数据库中未被AI返回的章节
        from sqlalchemy import and_, not_
        Chapter.query.filter(
            Chapter.project_id == project_id,
            not_(Chapter.chapter_number.in_(ai_numbers))
        ).delete(synchronize_session=False)
        db.session.commit()
        # upsert AI返回的所有章节
        for idx, ch in enumerate(ai_chapters):
            chapter_number = ch.get('chapterNumber') or ch.get('chapter_number') or ch.get('id')
            title = ch.get('title') or '未命名章节'
            content = ch.get('content', '')
            parent_id = ch.get('parent_id') or ch.get('parentId')
            db_chapter = Chapter.query.filter(and_(Chapter.project_id==project_id, Chapter.chapter_number==chapter_number)).first()
            if db_chapter:
                db_chapter.title = title
                db_chapter.content = content
                db_chapter.parent_id = parent_id
                db_chapter.order_index = idx
            else:
                db_chapter = Chapter(
                    project_id=project_id,
                    chapter_number=chapter_number,
                    title=title,
                    content=content,
                    parent_id=parent_id,
                    order_index=idx
                )
                db.session.add(db_chapter)
        db.session.commit()
        # 组织返回数据（只返回数据库中的章节）
        # 读取数据库中的所有章节（再次确认）
        all_db_chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
        db_chapters_full = [
            {
                'id': ch.id,
                'chapter_number': ch.chapter_number,
                'title': ch.title,
                'content': ch.content,
                'parent_id': ch.parent_id,
                'order_index': ch.order_index
            }
            for ch in all_db_chapters
        ]
        response = {
            'success': True,
            'data': {'chapters': db_chapters_full},
            'template': {
                'id': template.id,
                'title': template.title
            },
            'timestamp': datetime.now().isoformat()
        }
        print("\n" + "=" * 80)
        print("【后端调试】数据库读取到的章节:")
        print(json.dumps(db_chapters_full, ensure_ascii=False, indent=2))
        print("【后端调试】最终发送给前端的数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        print("=" * 80 + "\n")
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"生成大纲失败: {str(e)}")
        logger.error(f"错误详情:\n{error_trace}")
        
        # 检查是否是JSON解析错误
        if "'\n  \"chapters\"'" in str(e) or '"\n  "chapters""' in str(e):
            logger.error("可能是JSON解析错误，尝试获取原始响应")
            try:
                # 尝试捕获最后一次模型调用的原始响应
                if hasattr(ModelCaller, '_last_raw_response'):
                    last_response = getattr(ModelCaller, '_last_raw_response')
                    logger.error(f"最后一次模型原始响应(前100字符): {last_response[:100]}")
            except Exception as debug_error:
                logger.error(f"尝试获取原始响应时出错: {str(debug_error)}")
        
        return internal_error(f"生成大纲失败: {str(e)}")


@bp.route('/outlines/regenerate', methods=['POST'])
def regenerate_outline():
    """
    重新生成章节大纲
    请求体应包含:
    - template_id: 模板ID
    - requirement: 用户对重新生成的特殊要求（可选）
    - preserved_chapters: 希望保留的章节列表（可选）
    - input_file: 输入文件（可选）
    """
    try:
        # 获取参数
        data = request.get_json() or {}
        
        # 检查表单数据
        if not data and request.form:
            template_id = request.form.get('template_id')
            requirement = request.form.get('requirement', '')
            preserved_chapters_json = request.form.get('preserved_chapters', '[]')
            try:
                preserved_chapters = json.loads(preserved_chapters_json)
            except json.JSONDecodeError:
                preserved_chapters = []
        else:
            template_id = data.get('template_id')
            requirement = data.get('requirement', '')
            preserved_chapters = data.get('preserved_chapters', [])
        
        if not template_id:
            return bad_request('必须提供模板ID')
        
        template = Document.query.get(template_id)
        if not template:
            return not_found(f'未找到ID为{template_id}的模板')
        
        # 处理上传的输入文件（复用之前的代码）
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
                    elif content_type == 'text/plain':
                        file_ext = '.txt'
                    elif content_type == 'application/pdf':
                        file_ext = '.pdf'
                    # 可以根据需要添加更多文件类型
                
                # 生成唯一文件名
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{file_ext}"
                
                # 确保上传目录存在
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'inputs')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 保存文件
                input_file_path = os.path.join(upload_folder, unique_filename)
                input_file.save(input_file_path)
                logger.info(f"已保存输入文件: {input_file_path}")
        
        # 准备重新生成配置
        regenerate_config = {}
        if preserved_chapters:
            regenerate_config['preserved_chapters'] = preserved_chapters
        
        # 调用AI服务重新生成大纲
        ai_service = get_ai_service()
        result = ai_service.regenerate_document_outline(
            template_id, 
            input_file_path,
            requirement,
            regenerate_config
        )
        
        # === 新逻辑：将AI生成的新章节先写入数据库 ===
        from app.models.project import Chapter
        # 1. 先删除该项目下原有章节（如需保留用户指定章节可做特殊处理）
        project_id = template.project_id if hasattr(template, 'project_id') else None
        if not project_id and 'project_id' in data:
            project_id = data['project_id']
        if not project_id:
            return bad_request('无法确定project_id，无法保存章节')
        # 若有preserved_chapters，先获取其chapter_number
        preserved_numbers = set()
        if preserved_chapters:
            preserved_numbers = set([ch.get('chapter_number') or ch.get('chapterNumber') for ch in preserved_chapters])
        # 删除未保留的章节
        all_chapters = Chapter.query.filter_by(project_id=project_id).all()
        for ch in all_chapters:
            if ch.chapter_number not in preserved_numbers:
                db.session.delete(ch)
        db.session.commit()
        # 2. 插入AI生成的新章节
        new_chapters = result.get('chapters', [])
        # 获取当前最大order_index
        max_order = db.session.query(db.func.max(Chapter.order_index)).filter_by(project_id=project_id).scalar() or 0
        for idx, ch in enumerate(new_chapters):
            chapter_number = ch.get('chapterNumber') or ch.get('chapter_number')
            if chapter_number in preserved_numbers:
                continue  # 跳过已保留的章节
            chapter = Chapter(
                project_id=project_id,
                chapter_number=chapter_number,
                title=ch.get('title'),
                content='',
                parent_id=None,
                order_index=max_order + idx + 1
            )
            db.session.add(chapter)
        db.session.commit()
        # 3. 从数据库读取所有章节，返回给前端
        all_db_chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
        db_chapters_full = [
            {
                'id': ch.id,
                'chapter_number': ch.chapter_number,
                'title': ch.title,
                'content': ch.content,
                'parent_id': ch.parent_id,
                'order_index': ch.order_index
            }
            for ch in all_db_chapters
        ]
        response = {
            'success': True,
            'data': {'chapters': db_chapters_full},
            'template': {
                'id': template.id,
                'title': template.title
            },
            'timestamp': datetime.now().isoformat()
        }
        
        
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"重新生成大纲失败: {str(e)}")
        logger.error(f"错误详情:\n{error_trace}")
        return internal_error(f"重新生成大纲失败: {str(e)}")


@bp.route('/outlines/generate-subchapters', methods=['POST'])
def generate_subchapters():
    """
    生成第3级和第4级子章节
    请求体应包含:
    - template_id: 模板ID
    - chapters: 现有章节列表，包含chapterNumber和title
    - input_file: (可选) 输入文件
    """
    try:
        # 检查必要的字段
        data = request.get_json()
        
        # 如果不是JSON格式，继续检查是否是form格式
        if data is None:
            template_id = request.form.get('template_id')
            chapters_data = request.form.get('chapters')
            if chapters_data:
                chapters = json.loads(chapters_data)
            else:
                return bad_request('必须提供现有章节列表')
        else:
            template_id = data.get('template_id')
            chapters = data.get('chapters', [])
        
        if not template_id:
            return bad_request('必须提供模板ID')
            
        if not chapters or not isinstance(chapters, list):
            return bad_request('必须提供有效的章节列表')
        
        template = Document.query.get(template_id)
        if not template:
            return not_found(f'未找到ID为{template_id}的模板')
        
        # 处理上传的输入文件（复用这部分代码）
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
        
        # 调用AI服务生成子章节
        ai_service = get_ai_service()
        ai_result = ai_service.generate_subchapters(template_id, chapters, input_file_path)
        # 如果AI结果是字符串，尝试解析为JSON
        if isinstance(ai_result, str):
            try:
                subchapters_result = json.loads(ai_result)
            except Exception as e:
                print(f"AI子章节响应不是合法JSON，原始内容: {ai_result}")
                return internal_error(f"AI子章节响应不是合法JSON: {e}")
        else:
            subchapters_result = ai_result
        
        # 1. 获取project_id（假设前端有传递，或可通过template查找）
        project_id = None
        # 优先从请求体获取
        if data and 'project_id' in data:
            project_id = data['project_id']
        # 或者从template对象获取
        if not project_id and hasattr(template, 'project_id'):
            project_id = template.project_id
        if not project_id:
            # 尝试从章节列表中推断
            if chapters and isinstance(chapters, list) and 'project_id' in chapters[0]:
                project_id = chapters[0]['project_id']
        if not project_id:
            return bad_request('无法确定project_id，无法保存章节')

        # 2. 先删除原有3/4级子章节（可选，视业务需求）
        from app.models.project import Chapter
        # 这里只是示例，实际可根据chapter_number规则删除
        # db.session.query(Chapter).filter(Chapter.project_id==project_id, Chapter.chapter_number.like('%.%.%')).delete(synchronize_session=False)
        # db.session.commit()

        # 3. 只处理3/4级子章节：先删后插
        def is_3_or_4_level(chap_num):
            return chap_num and str(chap_num).count('.') >= 2
        ai_chapters = [ch for ch in subchapters_result.get('chapters', []) if is_3_or_4_level(ch.get('chapterNumber'))]
        # 删除所有3/4级
        Chapter.query.filter(
            Chapter.project_id == project_id,
            Chapter.chapter_number.like('%.%.%')
        ).delete(synchronize_session=False)
        db.session.commit()
        # 插入AI返回的3/4级
        for idx, ch in enumerate(ai_chapters):
            chapter_number = ch.get('chapterNumber')
            title = ch.get('title')
            db_chapter = Chapter(
                project_id=project_id,
                chapter_number=chapter_number,
                title=title,
                content='',
                parent_id=None,
                order_index=idx
            )
            db.session.add(db_chapter)
        db.session.commit()
        # === 新增：全局order_index重排，保证顺序唯一 ===
        all_chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.chapter_number.asc()).all()
        for idx, ch in enumerate(all_chapters):
            ch.order_index = idx
        db.session.commit()

        # 4. 从数据库读取所有章节，返回给前端
        all_db_chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
        db_chapters_full = [
            {
                'id': ch.id,
                'chapter_number': ch.chapter_number,
                'title': ch.title,
                'content': ch.content,
                'parent_id': ch.parent_id,
                'order_index': ch.order_index
            }
            for ch in all_db_chapters
        ]
        response = {
            'success': True,
            'data': {'chapters': db_chapters_full},
            'template': {
                'id': template.id,
                'title': template.title
            },
            'timestamp': datetime.now().isoformat()
        }
        
        

        # 打印数据库读取出来的章节数据
        project_id = None
        if not project_id and isinstance(response, dict) and 'data' in response and 'project_id' in response['data']:
            project_id = response['data']['project_id']
        if project_id:
            try:
                from app.models.project import Chapter
                chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
                print("【后端调试】数据库读取出来的章节数据:")
                for ch in chapters:
                    ch_dict = {
                        'id': ch.id,
                        'chapter_number': ch.chapter_number,
                        'title': ch.title,
                        'content': ch.content,
                        'parent_id': ch.parent_id,
                        'order_index': ch.order_index
                    }
                    print(ch_dict)
            except Exception as e:
                print(f"【后端调试】获取数据库章节数据失败: {e}")
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"生成子章节失败: {str(e)}")
        logger.error(f"错误详情:\n{error_trace}")
        return internal_error(f"生成子章节失败: {str(e)}")
