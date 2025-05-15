import { ref } from 'vue'
import { PreviewState } from './types'

// 预览状态
const previewVisible = ref(false)
const previewTitle = ref('')
const previewDocId = ref<number|null>(null)
const previewFilePath = ref<string|null>(null)

export const previewState: PreviewState = {
  previewVisible,
  previewTitle,
  previewDocId,
  previewFilePath
}

// 预览模板
export async function previewTemplate(templateId: number | null) {
  if (!templateId) {
    throw new Error('模板ID不存在，无法预览')
  }
  
  try {
    // 获取模板预览路径（这里可以根据实际API调整）
    previewFilePath.value = `/api/templates/${templateId}/preview`
    previewTitle.value = '模板预览'
    previewVisible.value = true
  } catch (error) {
    console.error('预览模板失败:', error)
    throw error
  }
}

// 预览输入文件
export async function previewInputFile(inputFilePath: string | null) {
  if (!inputFilePath) {
    throw new Error('输入文件路径不存在，无法预览')
  }
  
  try {
    previewFilePath.value = inputFilePath
    previewTitle.value = '输入文件预览'
    previewVisible.value = true
  } catch (error) {
    console.error('预览输入文件失败:', error) 
    throw error
  }
}
