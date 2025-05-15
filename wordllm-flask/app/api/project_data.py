from app.api.project import bp as project_bp

# 所有项目相关API已迁移至 app/api/project/ 子包
# 请在主应用中使用 project_bp 进行蓝图注册

@bp.route('/documents/generate-content', methods=['POST'])
def generate_document_content():
    """
    生成文档内容
    请求体应包含:
    - template_id: 模板ID
    - chapters: 章节列表，包含chapterNumber和title
    - chapter_number: (可选) 指定要生成内容的章节编号，不提供则生成所有章节
    - input_file: (可选) 输入文件
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
            print('[后端调试] 使用 form 方式，template_id:', template_id, type(template_id))
            print('[后端调试] chapters_data:', chapters_data, type(chapters_data))
            print('[后端调试] chapter_number:', chapter_number, type(chapter_number))
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
            print('[后端调试] 使用 json 方式，template_id:', template_id, type(template_id))
            print('[后端调试] chapters:', chapters, type(chapters))
            print('[后端调试] chapter_number:', chapter_number, type(chapter_number))
            print('[后端调试] project_id:', project_id, type(project_id))
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
                db_chapter.content = content
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
                        db_chapter.content = content
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
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"生成文档内容失败: {str(e)}")
        logger.error(f"错误详情:\n{error_trace}")
        return internal_error(f"生成文档内容失败: {str(e)}")

@bp.route('/documents/chat', methods=['POST'])
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
                content = last_message.get('content', '')
                
                if '生成' in content or '撰写' in content:
                    ai_response['content'] = f"以下是我为'{chapter.get('title')}'章节生成的内容建议：\n\n## {chapter.get('title')}概述\n\n本章节主要介绍相关的核心概念、实施方法和评估标准。作为文档的重要组成部分，{chapter.get('title')}需要清晰明了地表达相关要求和规范。\n\n## 主要内容\n\n1. {chapter.get('title')}的定义和重要性\n2. 实施{chapter.get('title')}的最佳实践\n3. {chapter.get('title')}的评估标准\n4. 案例分析\n\n您可以根据需要修改或扩展这些内容。"
                elif '优化' in content or '改进' in content:
                    ai_response['content'] = f"针对'{chapter.get('title')}'章节，您可以考虑以下优化建议：\n\n1. 增加实际案例或数据支持论点\n2. 使用图表或表格提高内容直观性\n3. 确保术语一致性，特别是专业术语\n4. 添加参考资料或标准引用\n5. 检查逻辑结构，确保各部分衔接自然\n\n您希望我详细展开其中某一方面吗？"
                elif '扩展' in content:
                    ai_response['content'] = f"为'{chapter.get('title')}'章节扩展内容时，可以考虑以下方向：\n\n1. 行业最佳实践和标准\n2. 当前面临的挑战及解决方案\n3. 未来发展趋势和预测\n4. 不同场景下的应用案例\n5. 与其他章节的关联和影响\n\n这些方向可以帮助您丰富章节内容，使文档更加全面和专业。"
                else:
                    ai_response['content'] = f"关于'{chapter.get('title')}'章节，您提到的'{content[:20]}...'很重要。我建议从以下几个方面思考：\n\n1. 明确章节目标和受众\n2. 确定核心内容和关键信息\n3. 组织结构，逻辑清晰\n4. 语言风格保持一致性\n\n您需要我在其中某个方面提供更具体的帮助吗？"
        
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

@bp.route('/projects', methods=['POST'])
def create_project():
    """新建项目"""
    data = request.get_json() or {}
    title = data.get('title')
    template_id = data.get('template_id')
    if not title:
        return bad_request('必须提供项目名称')
    project = Project(title=title, template_id=template_id)
    db.session.add(project)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': project.id, 'title': project.title, 'template_id': project.template_id}})

@bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目基本信息，包括模板ID"""
    project = Project.query.get(project_id)
    if not project:
        return not_found('项目不存在')
    project_data = {
        'id': project.id,
        'title': project.title,
        'template_id': project.template_id,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None
    }
    return jsonify({'success': True, 'data': project_data})

@bp.route('/projects/<int:project_id>/chapters', methods=['GET'])
def get_project_chapters(project_id):
    """获取项目下所有章节"""
    project = Project.query.get(project_id)
    if not project:
        return not_found('项目不存在')
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
    chapter_dicts = [
        {'id': c.id, 'chapter_number': c.chapter_number, 'title': c.title, 'content': c.content, 'parent_id': c.parent_id, 'order_index': c.order_index} for c in chapters
    ]
    print("【后端调试】数据库读取出来的章节数据:")
    for ch in chapter_dicts:
        print(ch)
    return jsonify({'success': True, 'data': chapter_dicts})

@bp.route('/projects/<int:project_id>/chapters', methods=['POST'])
def save_project_chapters(project_id):
    """批量保存章节：先清空该项目所有章节，再插入新章节"""
    data = request.get_json() or {}
    chapters = data.get('chapters', [])
    print("【后端调试】收到批量保存章节请求，chapters:")
    for ch in chapters:
        print(ch)
    if not isinstance(chapters, list) or not chapters:
        return bad_request('必须提供章节列表')
    # 先删除该项目下所有章节
    Chapter.query.filter_by(project_id=project_id).delete()
    db.session.commit()
    # 再批量插入
    new_ids = []
    written_chapters = []
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
        db.session.flush()  # 获取id
        new_ids.append(chapter.id)
        written_chapters.append({
            'id': chapter.id,
            'chapter_number': chapter.chapter_number,
            'title': chapter.title,
            'content': chapter.content,
            'parent_id': chapter.parent_id,
            'order_index': chapter.order_index
        })
    db.session.commit()
    print("【后端调试】实际写入数据库的章节:")
    for ch in written_chapters:
        print(ch)
    return jsonify({'success': True, 'data': {'ids': new_ids}})

@bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    """编辑章节内容"""
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return not_found('章节不存在')
    data = request.get_json() or {}
    chapter.title = data.get('title', chapter.title)
    chapter.content = data.get('content', chapter.content)
    chapter.order_index = data.get('order_index', chapter.order_index)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': chapter.id}})

@bp.route('/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """获取单个章节内容"""
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

# 注册API蓝图
def init_app(app):
    """初始化文档API模块"""
    app.register_blueprint(bp, url_prefix='/api')
