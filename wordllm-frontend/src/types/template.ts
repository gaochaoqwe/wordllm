export interface Template {
  id: number
  title?: string
  originalFilename: string
  fileSize: number
  fileType: string
  content?: string
  status: TemplateStatus
  created_at: string
  updated_at: string
  // 自定义提示词字段
  outline_prompt?: string
  subchapter_prompt?: string
  content_prompt?: string
}

export type TemplateStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'ERROR'

export interface TemplateSearchParams {
  title?: string
  page: number
  size: number
}

// 为了兼容API类型，将PageResponse移到了api.ts文件中
// export interface PageResponse<T> {
//   content: T[]
//   totalElements: number
//   totalPages: number
//   size: number
//   number: number
// }
