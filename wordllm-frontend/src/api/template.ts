import type { ApiResponse, PageResponse } from '@/types/api'
import type { Template, TemplateSearchParams } from '@/types/template'
import request from '@/utils/request'
import type { AxiosError } from 'axios'

export const api = {
  async uploadTemplate(
    file: File,
    title?: string,
    description?: string,
    outline_prompt?: string,
    subchapter_prompt?: string,
    content_prompt?: string
  ): Promise<Template> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }
    if (description) {
      formData.append('content', description)
    }
    if (outline_prompt) {
      formData.append('outline_prompt', outline_prompt)
    }
    if (subchapter_prompt) {
      formData.append('subchapter_prompt', subchapter_prompt)
    }
    if (content_prompt) {
      formData.append('content_prompt', content_prompt)
    }
    const response = await request.post<ApiResponse<Template>>('/templates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async getTemplate(id: string | number): Promise<Template> {
    const response = await request.get<ApiResponse<Template>>(`/templates/${id}`)
    return response.data
  },

  async getTemplatePreview(id: string | number): Promise<{content: string}> {
    const response = await request.get<ApiResponse<{content: string}>>(`/templates/${id}/preview`)
    return response.data
  },

  async searchTemplates(params: TemplateSearchParams): Promise<PageResponse<Template>> {
    console.log('[TemplateAPI] 调用 searchTemplates，参数:', params)
    try {
      const response = await request.get<PageResponse<Template>>('/templates', {
        params: {
          title: params.title || '',
          page: Math.max(0, params.page - 1),  // 确保页码从 0 开始
          size: params.size || 10
        }
      })

      console.log('[TemplateAPI] 获取到响应数据:', response)

      if (!response || !Array.isArray(response.content)) {
        console.error('[TemplateAPI] 响应数据格式不正确:', {
          response,
          hasContent: !!response?.content,
          isArray: Array.isArray(response?.content)
        })
        throw new Error('返回的数据格式不正确')
      }

      console.log('[TemplateAPI] 处理后的分页数据:', {
        content: response.content,
        totalElements: response.totalElements,
        totalPages: response.totalPages,
        size: response.size,
        number: response.number
      })

      return response
    } catch (error) {
      const axiosError = error as AxiosError
      console.error('[TemplateAPI] 搜索模板失败:', {
        message: axiosError.message,
        response: axiosError.response?.data,
        status: axiosError.response?.status
      })
      throw error
    }
  },

  async downloadTemplate(id: string | number): Promise<Blob> {
    const response = await request.get(`/templates/${id}/download`, {
      responseType: 'blob'
    })
    return response.data
  },

  async deleteTemplate(id: string | number): Promise<void> {
    await request.delete(`/templates/${id}`)
  },

  async updateTemplate(id: string | number, data: Partial<Template>): Promise<Template> {
    const response = await request.put<ApiResponse<Template>>(`/templates/${id}`, data)
    return response.data
  },

  async createTemplate(data: Partial<Template>): Promise<Template> {
    const response = await request.post<ApiResponse<Template>>('/templates', data)
    return response.data
  },

  getDownloadUrl(id: string | number): string {
    return `/api/templates/${id}/download`
  },

  getPreviewUrl(id: string | number): string {
    return `/api/templates/${id}/preview`
  }
}

export default api
