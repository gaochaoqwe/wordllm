from flask import request, jsonify, current_app, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
import uuid
from app.api import bp
from app.api.error import bad_request, not_found, internal_error
from app.models.document import Document
from app import db
from app.utils.logger import logger
import datetime
import mammoth
import base64
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/templates', methods=['GET'])
def get_templates():
    """获取所有模板列表，支持分页"""
    title = request.args.get('title', '')
    page = int(request.args.get('page', 0))
    size = int(request.args.get('size', 10))
    
    # 构建查询
    query = Document.query
    if title:
        query = query.filter(Document.title.like(f'%{title}%'))
    
    # 排序
    query = query.order_by(Document.updated_at.desc())
    
    # 计算总数
    total_elements = query.count()
    total_pages = (total_elements + size - 1) // size if size > 0 else 0
    
    # 执行分页查询
    templates = query.offset(page * size).limit(size).all()
    
    # 构建分页响应
    response = {
        'content': [doc.to_dict() for doc in templates],
        'totalElements': total_elements,
        'totalPages': total_pages,
        'size': size,
        'number': page,
        'last': page >= total_pages - 1 if total_pages > 0 else True
    }
    
    return jsonify(response)

@bp.route('/templates/<int:id>', methods=['GET'])
def get_template(id):
    """获取指定ID的模板"""
    template = Document.query.get(id)
    if not template:
        return not_found('模板不存在')
    return jsonify(template.to_dict())

@bp.route('/templates', methods=['POST'])
def create_template():
    """创建新模板"""
    data = request.get_json() or {}
    if 'title' not in data:
        return bad_request('必须包含title字段')
    
    template = Document(
        title=data.get('title'),
        content=data.get('content', ''),
        status=data.get('status', 'PENDING')
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201

@bp.route('/templates/<int:id>', methods=['PUT'])
def update_template(id):
    """更新模板"""
    print(f"【接收请求-PUT】模板ID={id}")
    template = Document.query.get(id)
    if not template:
        print(f"【错误】模板不存在: id={id}")
        return not_found('模板不存在')
    
    # 记录更新前的模板状态
    print(f"【更新前】模板状态: id={template.id}, title={template.title}, outline_prompt={template.outline_prompt}")
    
    data = request.get_json() or {}
    print(f"【请求数据】: {data}")
    
    if 'title' in data:
        print(f"【更新字段】title: {template.title} -> {data['title']}")
        template.title = data['title']
    if 'content' in data:
        print(f"【更新字段】content: 从{len(template.content) if template.content else 0}字符 -> {len(data['content']) if data['content'] else 0}字符")
        template.content = data['content']
    if 'status' in data:
        print(f"【更新字段】status: {template.status} -> {data['status']}")
        template.status = data['status']
    if 'outline_prompt' in data:
        print(f"【更新字段】outline_prompt: {template.outline_prompt} -> {data['outline_prompt']}")
        template.outline_prompt = data['outline_prompt']
    if 'subchapter_prompt' in data:
        print(f"【更新字段】subchapter_prompt: {template.subchapter_prompt} -> {data['subchapter_prompt']}")
        template.subchapter_prompt = data['subchapter_prompt']
    if 'content_prompt' in data:
        print(f"【更新字段】content_prompt: {template.content_prompt} -> {data['content_prompt']}")
        template.content_prompt = data['content_prompt']
    
    template.updated_at = datetime.datetime.now()
    
    # 记录更新后、提交前的模板状态
    print(f"【提交前】模板状态: id={template.id}, title={template.title}, outline_prompt={template.outline_prompt}")
    print(f"【检查】outline_prompt是否正确设置: {'是' if template.outline_prompt == data.get('outline_prompt') else '否'}")
    
    # 提交更改
    try:
        print(f"【开始提交】正在提交到数据库...")
        db.session.commit()
        print(f"【提交成功】数据库事务已提交")
    except Exception as e:
        print(f"【提交失败】数据库错误: {str(e)}")
        db.session.rollback()
        return internal_error(f"数据库更新失败: {str(e)}")
    
    # 验证更改是否真正保存
    print(f"【提交后检查】重新从数据库查询模板...")
    refreshed_template = Document.query.get(id)
    print(f"【确认结果】id={refreshed_template.id}, title={refreshed_template.title}")
    print(f"【确认结果】outline_prompt={refreshed_template.outline_prompt}")
    print(f"【存储检查】outline_prompt是否成功存入: {'成功' if refreshed_template.outline_prompt == data.get('outline_prompt') else '失败'}")
    
    # 返回给前端的内容
    response_data = template.to_dict()
    print(f"【返回前端】模板数据: outline_prompt={response_data.get('outline_prompt')}")
    return jsonify(response_data)

@bp.route('/templates/<int:id>', methods=['DELETE'])
def delete_template(id):
    """删除模板"""
    template = Document.query.get(id)
    if not template:
        return not_found('模板不存在')
    
    # 删除相关文件
    if template.file_path:
        # 先检查文件是否在template目录中
        upload_folder = current_app.config['UPLOAD_FOLDER']
        template_path = os.path.join(upload_folder, 'template', template.file_path)
        base_path = os.path.join(upload_folder, template.file_path)
        
        # 先尝试删除template目录中的文件
        if os.path.exists(template_path):
            try:
                os.remove(template_path)
                logger.info(f"成功删除文件: {template_path}")
            except Exception as e:
                logger.error(f"删除template目录中的文件失败: {e}")
        # 如果文件不在template目录，尝试删除基本目录中的文件
        elif os.path.exists(base_path):
            try:
                os.remove(base_path)
                logger.info(f"成功删除文件: {base_path}")
            except Exception as e:
                logger.error(f"删除基本目录中的文件失败: {e}")
        else:
            logger.warning(f"文件不存在: {template_path} 或 {base_path}")
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'message': '模板已删除'})

@bp.route('/templates/upload', methods=['POST'])
def upload_template():
    """上传模板文件"""
    # 检查请求中是否有文件
    if 'file' not in request.files:
        return bad_request('没有文件')
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return bad_request('没有选择文件')
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return bad_request(f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}')
    
    # 安全处理文件名
    logger.info(f"原始模板文件名: {file.filename}")
    original_filename = secure_filename(file.filename)
    logger.info(f"secure_filename后的模板文件名: {original_filename}")
    
    # 提取文件扩展名
    file_ext = os.path.splitext(original_filename)[1]
    logger.info(f"提取的模板文件扩展名: '{file_ext}'")
    
    # 如果没有扩展名，从content-type推断
    if not file_ext:
        content_type = file.content_type
        logger.info(f"模板文件的Content-Type: {content_type}")
        
        # 根据MIME类型推断扩展名
        if content_type == 'application/msword' or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_ext = '.docx'
            logger.info("从content-type推断模板扩展名.docx")
        elif content_type == 'text/plain':
            file_ext = '.txt'
            logger.info("从content-type推断模板扩展名.txt")
        elif content_type == 'application/pdf':
            file_ext = '.pdf'
            logger.info("从content-type推断模板扩展名.pdf")
        else:
            logger.warning(f"未知的模板content-type: {content_type}，使用.docx作为默认扩展名")
            file_ext = '.docx'  # 默认使用.docx
    
    # 生成唯一文件名 - 更简单的方式
    base_name = os.path.splitext(original_filename)[0]
    unique_filename = f"docx_{uuid.uuid4().hex}{file_ext}"
    logger.info(f"生成的唯一模板文件名: {unique_filename}")
    
    # 确保模板目录存在
    upload_folder = current_app.config['UPLOAD_FOLDER']
    template_folder = os.path.join(upload_folder, 'template')
    os.makedirs(template_folder, exist_ok=True)
    
    # 保存文件到template子目录
    file_path = os.path.join(template_folder, unique_filename)
    file.save(file_path)
    
    # 文件大小（字节）
    file_size = os.path.getsize(file_path)
    
    # 文件类型 - 使用已提取的file_ext
    file_type = file_ext[1:] if file_ext else ''  # 移除前导的.(点)
    
    # 获取模板名称和描述及自定义提示词
    template_name = request.form.get('title', original_filename)
    template_content = request.form.get('content', '')
    outline_prompt = request.form.get('outline_prompt', '')
    subchapter_prompt = request.form.get('subchapter_prompt', '')
    content_prompt = request.form.get('content_prompt', '')

    # 创建模板记录
    template = Document(
        title=template_name,
        content=template_content,  # 保存描述内容
        original_filename=original_filename,
        file_path=unique_filename,
        file_size=file_size,
        file_type=file_type,
        status='PENDING',
        outline_prompt=outline_prompt,
        subchapter_prompt=subchapter_prompt,
        content_prompt=content_prompt
    )
    
    db.session.add(template)
    db.session.commit()
    
    # 返回模板信息
    return jsonify(template.to_dict()), 201

@bp.route('/templates/<int:id>/download', methods=['GET'])
def download_template(id):
    """下载模板文件"""
    template = Document.query.get(id)
    if not template:
        return not_found('模板不存在')
    
    if not template.file_path:
        return bad_request('该模板没有关联的文件')
    
    # 构建文件路径 - 考虑文件可能保存在template子目录中
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 先检查文件是否在template目录中
    template_path = os.path.join(upload_folder, 'template', template.file_path)
    if os.path.exists(template_path):
        file_path = template_path
    
    # 验证文件是否存在
    if not os.path.exists(file_path):
        logger.error(f'文件不存在: {file_path}')
        return jsonify({'code': 404, 'message': '文件不存在'}), 404
    
    # 下载文件
    return send_from_directory(
        directory=os.path.dirname(file_path),
        path=os.path.basename(file_path),
        download_name=template.original_filename or os.path.basename(file_path),
        as_attachment=True
    )

@bp.route('/templates/<int:id>/preview', methods=['GET'])
def preview_template(id):
    """预览模板文件"""
    template = Document.query.get(id)
    if not template:
        return not_found('模板不存在')
    
    # 检查是否请求HTML格式
    html_format = request.args.get('format') == 'html'
    
    # 如果没有文件路径，尝试返回模板内容
    if not template.file_path:
        if template.content:
            return jsonify({'content': template.content})
        else:
            return bad_request('该模板没有关联的文件或内容')
    
    # 构建文件路径 - 使用更可靠的文件路径处理
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 检查是否早期存储的文件名（没有目录路径）
    if not os.path.sep in template.file_path:
        # 简单文件名，应该在template目录下
        file_path = os.path.join(upload_folder, 'template', template.file_path)
    else:
        # 已有完整路径
        if template.file_path.startswith('template/'):
            # 如果路径已经包含template前缀
            file_path = os.path.join(upload_folder, template.file_path)
        else:
            # 先检查完整路径
            direct_path = os.path.join(upload_folder, template.file_path)
            if os.path.exists(direct_path):
                file_path = direct_path
            else:
                # 尝试在template目录下查找
                file_path = os.path.join(upload_folder, 'template', template.file_path)
    
    # 打印所有可能的路径用于调试
    logger.info(f"模板 ID: {template.id}, 文件路径: {template.file_path}")
    logger.info(f"最终路径: {file_path}")
    logger.info(f"文件是否存在: {os.path.exists(file_path)}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return jsonify({'code': 404, 'message': '文件不存在'}), 404
    
    # 获取文件目录和文件名
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    # 处理文件格式
    # 添加调试日志，检查请求参数
    logger.info(f"请求参数: {request.args}")
    logger.info(f"HTML格式参数: format={request.args.get('format')}, html_format={html_format}")
    
    # 如果请求HTML格式且是DOCX文件，使用mammoth解析并返回HTML
    if html_format and template.file_type and template.file_type.lower() in ['docx', 'doc']:
        try:
            logger.info(f"Converting DOCX to HTML: {file_path}")
            
            # 自定义样式映射，更好地处理Word文档的样式
            style_map = """
                p[style-name='Title'] => h1:fresh
                p[style-name='Heading 1'] => h1:fresh
                p[style-name='Heading 2'] => h2:fresh
                p[style-name='Heading 3'] => h3:fresh
                p[style-name='Heading 4'] => h4:fresh
                p[style-name='Heading 5'] => h5:fresh
                p[style-name='Heading 6'] => h6:fresh
                r[style-name='Strong'] => strong
                r[style-name='Emphasis'] => em
                p[style-name='Quote'] => blockquote
                p[style-name='Normal'] => p
            """
            
            # 图片处理选项 - 内联base64格式
            def image_handler(image):
                with image.open() as image_bytes:
                    image_data = image_bytes.read()
                    encoded_image = base64.b64encode(image_data).decode("ascii")
                    return {"src": f"data:{image.content_type};base64,{encoded_image}"}
            
            # 使用mammoth转换DOCX为HTML
            with open(file_path, 'rb') as docx_file:
                result = mammoth.convert_to_html(
                    docx_file, 
                    style_map=style_map,
                    convert_image=mammoth.images.img_element(image_handler)
                )
            
            # 获取生成的HTML
            html_content = result.value
            
            # 添加基本样式包装
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{template.title}</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1, h2, h3, h4, h5, h6 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    p {{ margin-top: 0; margin-bottom: 16px; }}
                    img {{ max-width: 100%; }}
                    table {{ border-collapse: collapse; margin: 15px 0; width: 100%; }}
                    table, th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f8f8f8; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # 记录可能的警告
            if result.messages:
                logger.warning(f"Conversion warnings: {result.messages}")
            
            # 创建HTML响应
            response = make_response(styled_html)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            
            # 添加跨域和缓存控制头
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            # 返回HTML响应
            return response
            
        except Exception as e:
            logger.error(f"Error converting DOCX to HTML: {e}")
            return jsonify({
                'code': 500,
                'message': f'DOCX转HTML失败: {str(e)}'
            }), 500
    
    # 如果直接访问预览URL但没有指定format=html，尝试自动检测文件类型进行转换
    if template.file_type and template.file_type.lower() in ['docx', 'doc']:
        try:
            logger.info(f"自动转换DOCX为HTML: {file_path}")
            
            # 复用上面的转换逻辑...
            style_map = """
                p[style-name='Title'] => h1:fresh
                p[style-name='Heading 1'] => h1:fresh
                p[style-name='Heading 2'] => h2:fresh
                p[style-name='Heading 3'] => h3:fresh
                p[style-name='Heading 4'] => h4:fresh
                p[style-name='Heading 5'] => h5:fresh
                p[style-name='Heading 6'] => h6:fresh
                r[style-name='Strong'] => strong
                r[style-name='Emphasis'] => em
                p[style-name='Quote'] => blockquote
                p[style-name='Normal'] => p
            """
            
            # 图片处理选项 - 内联base64格式
            def image_handler(image):
                with image.open() as image_bytes:
                    image_data = image_bytes.read()
                    encoded_image = base64.b64encode(image_data).decode("ascii")
                    return {"src": f"data:{image.content_type};base64,{encoded_image}"}
            
            # 使用mammoth转换DOCX为HTML
            with open(file_path, 'rb') as docx_file:
                result = mammoth.convert_to_html(
                    docx_file, 
                    style_map=style_map,
                    convert_image=mammoth.images.img_element(image_handler)
                )
            
            # 获取生成的HTML
            html_content = result.value
            
            # 添加基本样式包装
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{template.title}</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1, h2, h3, h4, h5, h6 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    p {{ margin-top: 0; margin-bottom: 16px; }}
                    img {{ max-width: 100%; }}
                    table {{ border-collapse: collapse; margin: 15px 0; width: 100%; }}
                    table, th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f8f8f8; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # 创建HTML响应
            response = make_response(styled_html)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            
            # 添加跨域和缓存控制头
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            # 返回HTML响应
            return response
            
        except Exception as e:
            logger.error(f"自动转换DOCX到HTML失败: {e}")
            # 转换失败，继续使用原始文件返回
    
    # 如果上述情况都不满足，返回原始文件
    # 增加调试日志，输出文件路径信息
    logger.info(f"Serving original file: {file_path}")
    logger.info(f"Directory: {directory}, Filename: {filename}")
    
    try:
        # 设置一个查询参数来控制是否作为附件下载
        download_mode = request.args.get('download', 'false').lower() == 'true'
        
        # 读取文件内容，自定义响应头
        return send_from_directory(
            directory=directory,
            path=filename,
            download_name=template.original_filename or filename,
            as_attachment=download_mode,
            etag=True,
            max_age=0  # 避免缓存
        )
        response = make_response(file_content)
        
        # 设置正确的内容类型
        if template.file_type.lower() == 'docx':
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif template.file_type.lower() == 'pdf':
            response.headers['Content-Type'] = 'application/pdf'
        elif template.file_type.lower() == 'txt':
            response.headers['Content-Type'] = 'text/plain'
        else:
            response.headers['Content-Type'] = 'application/octet-stream'
        
        # 明确指定内联而非下载
        response.headers['Content-Disposition'] = 'inline; filename="{0}"'.format(filename)
        
        # 添加跨域和缓存控制头
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # 打印所有响应头信息供调试
        header_info = {key: value for key, value in response.headers.items()}
        logger.info(f"Response headers: {header_info}")
            
        return response
    except Exception as e:
        # 如果出错，试回通过绝对路径发送文件
        logger.error(f"Error serving file with send_from_directory: {e}")
        
        # 尝试直接读取文件并发送
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            response = make_response(file_content)
            
            # 设置正确的MIME类型
            if template.file_type.lower() == 'docx':
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif template.file_type.lower() == 'pdf':
                response.headers['Content-Type'] = 'application/pdf'
            elif template.file_type.lower() == 'txt':
                response.headers['Content-Type'] = 'text/plain'
            else:
                # 默认二进制
                response.headers['Content-Type'] = 'application/octet-stream'
                
            # 添加跨域和缓存控制头
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        except Exception as e2:
            logger.error(f"Failed to serve file directly: {e2}")
            return not_found(f"无法访问文件: {e2}")
