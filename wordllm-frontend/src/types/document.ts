export interface Document {
  id: number
  title?: string
  originalFilename: string
  fileSize: number
  fileType: string
  templateId?: number
  status: DocumentStatus
  createdAt: string
  updatedAt: string
  chapters?: Chapter[]
}

export type DocumentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'ERROR'

export interface DocumentSearchParams {
  title?: string
  page: number
  size: number
}

export interface PageResponse<T> {
  content: T[]
  totalElements: number
  totalPages: number
  size: number
  number: number
}

export interface Chapter {
  id: string
  title: string
  content?: string
  status: ChapterStatus
  currentWords: number
  requiredWords: number
  parentId?: string
  order?: number
}

export type ChapterStatus = 'confirmed' | 'unconfirmed' | 'writing' | 'unwritten'

export interface ChapterGenerateOptions {
  mode: 'quick' | 'precise'
  maxTokens?: number
  temperature?: number
  customPrompt?: string
}
