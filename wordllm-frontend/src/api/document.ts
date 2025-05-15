import type { ApiResponse, PageResponse, DocumentSearchParams } from '@/types/api'
import type { Document } from '@/types/document'
import request from '@/utils/request'
import type { AxiosError } from 'axios'

export const api = {
  async uploadDocument(file: File, title?: string): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }
    const response = await request.post<ApiResponse<Document>>('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async getDocument(id: string | number): Promise<Document> {
    const response = await request.get<ApiResponse<Document>>(`/documents/${id}`)
    return response.data
  },

  async searchDocuments(params: DocumentSearchParams): Promise<PageResponse<Document>> {
    console.log('[DocumentAPI] 调用 searchDocuments，参数:', params)
    try {
      const response = await request.get<PageResponse<Document>>('/documents', {
        params: {
          title: params.title || '',
          page: Math.max(0, params.page - 1),  // 确保页码从 0 开始
          size: params.size || 10
        }
      })

      console.log('[DocumentAPI] 获取到响应数据:', response)

      if (!response || !Array.isArray(response.content)) {
        console.error('[DocumentAPI] 响应数据格式不正确:', {
          response,
          hasContent: !!response?.content,
          isArray: Array.isArray(response?.content)
        })
        throw new Error('返回的数据格式不正确')
      }

      console.log('[DocumentAPI] 处理后的分页数据:', {
        content: response.content,
        totalElements: response.totalElements,
        totalPages: response.totalPages,
        size: response.size,
        number: response.number
      })

      return response
    } catch (error) {
      const axiosError = error as AxiosError
      console.error('[DocumentAPI] 搜索文档失败:', {
        message: axiosError.message,
        response: axiosError.response?.data,
        status: axiosError.response?.status
      })
      throw error
    }
  },

  async downloadDocument(id: string | number): Promise<Blob> {
    const response = await request.get(`/documents/${id}/download`, {
      responseType: 'blob'
    })
    return response.data
  },

  async deleteDocument(id: string | number): Promise<void> {
    await request.delete(`/documents/${id}`)
  },

  getDownloadUrl(id: string | number): string {
    return `/api/documents/${id}/download`
  },

  getPreviewUrl(id: string | number): string {
    return `/api/documents/${id}/preview`
  }
}

export default api
