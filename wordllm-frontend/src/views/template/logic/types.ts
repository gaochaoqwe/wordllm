/**
 * 模板管理相关类型定义
 */
import type { Ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Template } from '../../../types/template'

/**
 * 模板状态类型
 */
export interface TemplateState {
  // 列表状态
  loading: Ref<boolean>
  templates: Ref<Template[]>
  total: Ref<number>
  
  // 分页状态
  currentPage: Ref<number>
  pageSize: Ref<number>
  
  // 搜索状态
  searchTitle: Ref<string>
  
  // 弹窗状态
  formVisible: Ref<boolean>
  submitting: Ref<boolean>
  editMode: Ref<boolean>
  uploadNewFile: Ref<boolean>
  currentTemplate: Ref<Template | null>
  
  // 预览状态
  previewVisible: Ref<boolean>
  previewDocId: Ref<number | string>
  
  // 表单相关
  formRef: Ref<FormInstance | undefined>
  fileUploaderRef: Ref<unknown> // 改进any类型
  form: {
    id: number
    title: string
    content: string
    outline_prompt: string
    subchapter_prompt: string
    content_prompt: string
    file: File | null
  }
  rules: FormRules
}

/**
 * 模板API接口
 */
export interface TemplateApi {
  loadTemplates: () => Promise<void>
  getTemplatePreview: (templateId: number) => Promise<Record<string, unknown>>
  deleteTemplate: (templateId: number) => Promise<boolean>
  submitTemplateForm: () => Promise<boolean>
}

/**
 * 模板事件处理接口
 */
export interface TemplateEvents {
  handleSearch: () => void
  handleSizeChange: (size: number) => void
  handleCurrentChange: (page: number) => void
  handlePreview: (template: Template) => Promise<PreviewResult>
  handleAdd: () => void
  handleEdit: (template: Template) => void
  handleDelete: (template: Template) => Promise<boolean>
  handleFileChange: (file: File) => void
  resetForm: () => void
  submitForm: () => Promise<boolean>
}

/**
 * 预览结果类型
 */
export interface PreviewResult {
  action: 'navigate' | 'preview' | 'error'
  name?: string
  id?: number | string
  message?: string
}

/**
 * 模板管理结果类型
 */
export interface TemplateManager extends TemplateState, TemplateEvents, TemplateApi {
  formatDate: (dateStr?: string) => string
  formatFileSize: (size?: number) => string
}
