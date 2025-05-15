import request from '@/utils/request'

// 创建项目
export async function createProject(data: { 
  // 原有字段（为了兼容性保留）
  title?: string, 
  templateId?: number, 
  inputFile?: string,
  // 新增字段
  project_name?: string,  // 项目名称
  template_name?: string  // 模板名称
}) {
  // 后端 /api/projects 支持 POST 创建
  return await request.post('/projects', data)
}
