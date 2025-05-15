export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

export interface PageResponse<T> {
  content: T[]
  totalElements: number
  totalPages: number
  size: number
  number: number
  last: boolean
}

export interface TemplateSearchParams {
  title?: string
  page: number
  size?: number
}
