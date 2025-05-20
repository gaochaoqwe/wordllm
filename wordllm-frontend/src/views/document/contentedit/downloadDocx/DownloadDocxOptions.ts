import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { downloadDocx, ExportSettings } from './sevices/downloadDocxService'

// 全局设置状态
const exportSettings = ref<ExportSettings>({
  format: 'docx',
  scope: 'all',
  margins: {
    top: 2.54,
    bottom: 2.54,
    left: 3.18,
    right: 3.18
  },
  section_number_style: {
    number_style: 'chapter'
  }
})

/**
 * 获取当前项目ID
 */


/**
 * 处理取消操作
 */
export function onCancel() {
  console.log('[DownloadDocxOptions] 用户取消')
}

/**
 * 收集所有组件的设置并执行下载
 */
export async function onConfirm(projectId: number, chapterNumber?: number) {
  console.log('[DownloadDocxOptions] 用户确定，收集设置')
  if (!projectId) {
    ElMessage.error('无法获取项目ID，请返回项目页面重试')
    return false
  }
  // 如果是当前章节模式，获取当前章节编号
  if (exportSettings.value.scope === 'current') {
    if (chapterNumber) {
      exportSettings.value.currentChapter = chapterNumber
    } else {
      ElMessage.warning('无法获取当前章节编号，将下载所有章节')
      exportSettings.value.scope = 'all'
    }
  }
  try {
    await downloadDocx(projectId, exportSettings.value)
    return true
  } catch (error) {
    console.error('[DownloadDocxOptions] 下载失败:', error)
    ElMessage.error('下载失败，请重试')
    return false
  }
}

export { exportSettings }
