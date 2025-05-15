/**
 * 模板管理主入口
 * 组合所有模块，提供统一的模板管理功能
 */
import { onMounted } from 'vue'
import type { TemplateManager } from './types'

// 导入各个模块
import { createTemplateState } from './modules/templateState'
import { createTemplateApi } from './modules/templateApi'
import { createTemplateEvents } from './modules/templateEvents'
import { formatDate, formatFileSize } from './modules/templateUtils'

/**
 * 模板管理逻辑组合函数
 * 使用组合模式整合各个功能模块
 */
export function useTemplateManager(): TemplateManager {
  // 创建状态管理模块
  const state = createTemplateState()
  
  // 创建API交互模块
  const api = createTemplateApi(state)
  
  // 创建事件处理模块
  const events = createTemplateEvents(state, api)
  
  // 页面加载时自动获取模板列表
  onMounted(() => {
    api.loadTemplates()
  })
  
  // 组合所有模块导出
  return {
    // 状态模块
    ...state,
    
    // API模块
    ...api,
    
    // 事件处理模块
    ...events,
    
    // 工具函数
    formatDate,
    formatFileSize
  }
}
