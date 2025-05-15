import request from '@/utils/request'
import type { Chapter, ChapterGenerateOptions } from '@/types/document'

export const chapterApi = {
  // 获取文档的所有章节
  async getChapters(documentId: string | number): Promise<Chapter[]> {
    const response = await request.get(`/documents/${documentId}/chapters`)
    return response.data
  },

  // 获取单个章节内容
  async getChapter(documentId: string | number, chapterId: string): Promise<Chapter> {
    const response = await request.get(`/documents/${documentId}/chapters/${chapterId}`)
    return response.data
  },

  // 生成章节内容
  async generateChapter(
    documentId: string | number,
    chapterId: string,
    options: ChapterGenerateOptions
  ): Promise<void> {
    await request.post(`/documents/${documentId}/chapters/${chapterId}/generate`, options)
  },

  // 批量生成章节
  async batchGenerate(documentId: string | number, options: ChapterGenerateOptions): Promise<void> {
    await request.post(`/documents/${documentId}/chapters/batch-generate`, options)
  },

  // 更新章节内容
  async updateChapter(
    documentId: string | number,
    chapterId: string,
    chapter: Partial<Chapter>
  ): Promise<Chapter> {
    const response = await request.put(
      `/documents/${documentId}/chapters/${chapterId}`,
      chapter
    )
    return response.data
  },

  // 删除章节
  async deleteChapter(documentId: string | number, chapterId: string): Promise<void> {
    await request.delete(`/documents/${documentId}/chapters/${chapterId}`)
  },

  // 更新章节顺序
  async updateChapterOrder(
    documentId: string | number,
    chapterIds: string[]
  ): Promise<void> {
    await request.put(`/documents/${documentId}/chapters/order`, { chapterIds })
  },

  // 导出文档大纲
  async exportOutline(documentId: string | number): Promise<Blob> {
    const response = await request.get(`/documents/${documentId}/outline/export`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export default chapterApi
