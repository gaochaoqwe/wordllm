from flask import request, jsonify
from app.models.project import Project
from app import db
from app.api.error import bad_request, not_found

# 项目主路由

def create_project():
    data = request.get_json() or {}
    
    # 获取前端传来的参数
    project_name = data.get('project_name')
    template_name = data.get('template_name') or data.get('title')  # 兼容旧代码，允许用title传模板名称
    
    # 兼容 templateId (前端) 和 template_id (后端)
    template_id = data.get('template_id') or data.get('templateId')
    
    # 参数校验
    if not project_name:
        return bad_request('必须提供项目名称')
    if not template_name:
        return bad_request('必须提供模板名称')
    if not template_id:
        return bad_request('必须提供模板ID')
    
    # 创建项目
    project = Project(
        project_name=project_name,
        template_name=template_name,
        template_id=template_id
    )
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {
            'id': project.id,
            'project_name': project.project_name,
            'template_name': project.template_name,
            'template_id': project.template_id
        }
    })


def get_project(project_id):
    print(f"[后端调试] 获取项目详情: project_id = {project_id}")
    project = Project.query.get(project_id)
    if not project:
        print(f"[后端调试] 项目不存在: project_id = {project_id}")
        return not_found('项目不存在')
    
    # 兼容性处理: 如果项目仍在使用旧的数据结构
    has_new_fields = hasattr(project, 'project_name') and hasattr(project, 'template_name')
    
    if has_new_fields:
        print(f"[后端调试] 找到项目: id={project.id}, project_name={project.project_name}, "
              f"template_name={project.template_name}, template_id={project.template_id}")
    else:
        # 兼容旧模型
        print(f"[后端调试] 找到项目(旧模型): id={project.id}, title={project.title}, "
              f"template_id={project.template_id}")
    
    if not project.template_id:
        print(f"[后端调试] 警告: 项目没有template_id, 这将导致生成文档失败")
    
    # 构建响应数据，兼容新旧字段
    project_data = {
        'id': project.id,
        'template_id': project.template_id,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None
    }
    
    # 根据不同版本模型添加相应字段
    if has_new_fields:
        project_data['project_name'] = project.project_name
        project_data['template_name'] = project.template_name
        # 为了兼容性，还是返回 title
        project_data['title'] = project.template_name
    else:
        # 兼容旧版本
        project_data['title'] = project.title
        # 对于旧版本，将title同时返回为template_name
        project_data['template_name'] = project.title
        # 旧版本没有project_name，使用title作为默认值
        project_data['project_name'] = project.title
    
    print(f"[后端调试] 返回项目详情: {project_data}")
    return jsonify({'success': True, 'data': project_data})

def get_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 更新搜索参数，支持对项目名称或模板名称进行搜索
    search_term = request.args.get('search', None, type=str)
    search_title = request.args.get('title', None, type=str)  # 兼容旧参数
    search_project_name = request.args.get('project_name', None, type=str)
    search_template_name = request.args.get('template_name', None, type=str)

    query = Project.query
    
    # 检查是否存在新字段（检查第一条记录）
    has_new_fields = False
    first_project = Project.query.first()
    if first_project:
        has_new_fields = hasattr(first_project, 'project_name') and hasattr(first_project, 'template_name')

    # 根据不同的模型应用不同的搜索逻辑
    if has_new_fields:
        # 使用新字段进行搜索
        if search_term:  # 通用搜索条件，匹配项目名或模板名
            query = query.filter(
                db.or_(
                    Project.project_name.ilike(f'%{search_term}%'),
                    Project.template_name.ilike(f'%{search_term}%')
                )
            )
        if search_project_name:  # 仅搜索项目名称
            query = query.filter(Project.project_name.ilike(f'%{search_project_name}%'))
        if search_template_name:  # 仅搜索模板名称
            query = query.filter(Project.template_name.ilike(f'%{search_template_name}%'))
        if search_title:  # 兼容旧版搜索，将其应用于模板名称
            query = query.filter(Project.template_name.ilike(f'%{search_title}%'))
    else:
        # 对旧模型使用title字段
        if search_term or search_title or search_project_name or search_template_name:
            search_value = search_term or search_title or search_project_name or search_template_name
            query = query.filter(Project.title.ilike(f'%{search_value}%'))

    query = query.order_by(Project.created_at.desc())
    paginated_projects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    projects_data = []
    
    for project in paginated_projects.items:
        project_item = {
            'id': project.id,
            'template_id': project.template_id,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None
        }
        
        # 根据不同的模型结构返回不同的字段
        if has_new_fields:
            project_item['project_name'] = project.project_name
            project_item['template_name'] = project.template_name
            # 为了向后兼容仍然返回 title
            project_item['title'] = project.template_name
        else:
            project_item['title'] = project.title
            # 旧字段兼容新字段
            project_item['template_name'] = project.title
            project_item['project_name'] = project.title
        
        projects_data.append(project_item)

    return jsonify({
        'success': True,
        'data': projects_data,
        'total': paginated_projects.total,
        'pages': paginated_projects.pages,
        'current_page': paginated_projects.page,
        'per_page': paginated_projects.per_page,
        'has_next': paginated_projects.has_next,
        'has_prev': paginated_projects.has_prev
    })
