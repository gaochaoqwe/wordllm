import { ref } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { RegenerateState } from './types'
import { outlineState } from './outlineState'
import { saveChaptersToDB } from './apiService'

// 重新生成相关的状态
// 初始化为false，确保页面首次加载时不会显示对话框
const isRegenerating = ref(false)
const regenerateRequirement = ref('')

export const regenerateState: RegenerateState = {
  isRegenerating,
  regenerateRequirement
}

// 重新生成章节菜单的主函数
export async function regenerate() {
  // 显示自定义要求输入框
  isRegenerating.value = true
}

// 实际执行重新生成大纲的函数
export async function regenerateChapters(preserveEdited = false) {
  if (!outlineState.projectId.value || !outlineState.templateId.value) {
    ElMessage.error('项目ID或模板ID不存在，无法重新生成')
    return
  }
  
  isRegenerating.value = false // 关闭输入框
  
  // 显示加载指示器
  const loading = ElLoading.service({
    lock: true,
    text: '正在重新生成章节目录...',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  
  try {
    // 准备请求参数
    const params = new URLSearchParams()
    params.append('template_id', String(outlineState.templateId.value))
    params.append('project_id', outlineState.projectId.value)
    
    // 如果有自定义要求，也加入参数
    if (regenerateRequirement.value) {
      params.append('requirement', regenerateRequirement.value)
    }
    
    // 如果要保留用户编辑的部分，则传递当前章节数据
    if (preserveEdited && outlineState.chapters.value.length > 0) {
      params.append('preserveEdited', 'true')
      params.append('currentChapters', JSON.stringify(outlineState.chapters.value))
    }
    
    // 调用API重新生成大纲
    const response = await fetch(`/api/outlines/regenerate?${params.toString()}`)
    const result = await response.json()
    
    if (!result.success) {
      throw new Error(result.message || '重新生成大纲失败')
    }
    
    // 更新章节数据
    if (result.data && Array.isArray(result.data.chapters)) {
      outlineState.chapters.value = result.data.chapters
      ElMessage.success('章节大纲已重新生成')
      
      // 保存到数据库
      await saveChaptersToDB()
    } else {
      throw new Error('返回数据格式不正确')
    }
  } catch (error) {
    console.error('重新生成大纲失败:', error)
    ElMessage.error(`重新生成大纲失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    // 关闭加载指示器
    loading.close()
    // 重置自定义要求
    regenerateRequirement.value = ''
  }
}

// 子章节重新生成
export async function regenerateSubchapters() {
  // 可以根据具体需求实现子章节重新生成逻辑
  ElMessage.info('子章节重新生成功能正在开发中')
}
