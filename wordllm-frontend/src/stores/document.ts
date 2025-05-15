import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Document, DocumentSearchParams } from '@/types/document'
import { api as documentApi } from '@/api/document'
import { ElMessage } from 'element-plus'

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function searchDocuments(params: DocumentSearchParams) {
    try {
      loading.value = true
      console.log('[DocumentStore] 开始搜索模板，参数:', params)

      const pageData = await documentApi.searchDocuments({
        title: params.title || '',
        page: params.page,
        size: params.size || 10
      })

      console.log('[DocumentStore] 获取到分页数据:', {
        documentsCount: pageData.content.length,
        totalElements: pageData.totalElements,
        currentPage: pageData.number + 1
      })
      
      documents.value = pageData.content
      total.value = pageData.totalElements
      
      if (documents.value.length === 0) {
        ElMessage.info('没有找到匹配的模板')
      }
    } catch (error: any) {
      console.error('[DocumentStore] 搜索模板失败:', {
        message: error.message,
        response: error.response?.data
      })
      ElMessage.error(error.message || '获取模板列表失败')
      documents.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(file: File, title?: string) {
    try {
      const document = await documentApi.uploadDocument(file, title)
      if (document) {
        documents.value.unshift(document)
        total.value++
        ElMessage.success('模板上传成功')
        return document
      }
    } catch (error: any) {
      console.error('Failed to upload template:', error)
      ElMessage.error(error.message || '模板上传失败')
      throw error
    }
  }

  async function downloadDocument(id: number) {
    try {
      const blob = await documentApi.downloadDocument(id)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'document.docx') // 你可能想要从响应头中获取实际的文件名
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error('Failed to download template:', error)
      ElMessage.error(error.message || '下载模板失败')
      throw error
    }
  }

  async function deleteDocument(id: number) {
    try {
      await documentApi.deleteDocument(id)
      const index = documents.value.findIndex(doc => doc.id === id)
      if (index > -1) {
        documents.value.splice(index, 1)
        total.value--
      }
      ElMessage.success('模板删除成功')
    } catch (error: any) {
      console.error('Failed to delete template:', error)
      ElMessage.error(error.message || '模板删除失败')
      throw error
    }
  }

  return {
    documents,
    total,
    loading,
    searchDocuments,
    uploadDocument,
    downloadDocument,
    deleteDocument
  }
})
