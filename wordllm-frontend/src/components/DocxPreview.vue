<template>
  <div class="docx-preview">
    <!-- 预览对话框 -->
    <el-dialog
      v-if="dialogMode"
      v-model="dialogVisible"
      :title="dialogTitle || '文档预览'"
      width="75%"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <div class="preview-container" :style="{ height: dialogMode ? '70vh' : height }">
        <!-- 预览内容 -->
        <div class="content-container" :style="{ height: dialogMode ? '65vh' : height }">
          <!-- 加载中状态 -->
          <div v-if="loading" class="loading-state">
            <el-skeleton :rows="10" animated />
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="error" class="error-state">
            <el-empty :description="error">
              <template #image>
                <el-icon class="empty-icon" :size="48" color="#F56C6C"><warning-filled /></el-icon>
              </template>
            </el-empty>
          </div>
          
          <!-- 空状态 -->
          <div v-else-if="!documentUrl && !htmlContent" class="empty-state">
            <el-empty description="暂无内容可预览">
              <template #image>
                <el-icon class="empty-icon" :size="48"><document /></el-icon>
              </template>
            </el-empty>
          </div>
          
          <!-- 内容区域 -->
          <div v-else class="content" v-html="htmlContent"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 内联模式 -->
    <div v-else class="inline-preview">
      <!-- 内容容器 -->
      <div class="content-container" :style="{ height: height }">
        <!-- 加载中状态 -->
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <el-empty :description="error">
            <template #image>
              <el-icon class="empty-icon" :size="48" color="#F56C6C"><warning-filled /></el-icon>
            </template>
          </el-empty>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="!documentUrl && !htmlContent" class="empty-state">
          <el-empty description="暂无内容可预览">
            <template #image>
              <el-icon class="empty-icon" :size="48"><document /></el-icon>
            </template>
          </el-empty>
        </div>
        
        <!-- 内容区域 -->
        <div v-else ref="contentRef" class="content"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

import { WarningFilled, Document } from '@element-plus/icons-vue'

// 组件props定义
const props = defineProps({
  // 对话框模式标题
  dialogTitle: {
    type: String,
    default: '文档预览'
  },
  // 是否使用对话框模式
  dialogMode: {
    type: Boolean,
    default: false
  },
  // 对话框是否可见 (仅在dialogMode=true时有效)
  modelValue: {
    type: Boolean,
    default: false
  },
  // 文档ID
  documentId: {
    type: [Number, String],
    default: null
  },
  // 文档URL
  documentUrl: {
    type: String,
    default: ''
  },
  // HTML内容
  htmlContent: {
    type: String,
    default: ''
  },
  // 高度 (内联模式有效)
  height: {
    type: String,
    default: '500px'
  },
  // 自动加载
  autoLoad: {
    type: Boolean,
    default: true
  }
})

// 组件事件
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'load', success: boolean): void
  (e: 'error', message: string): void
  (e: 'close'): void
}>()

// 组件内部状态
const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const error = ref('')
const htmlContent = ref('')

// 计算得到的URL，添加HTML格式参数
const documentUrl = computed(() => {
  if (!props.documentUrl) return ''
  
  try {
    // 确保URL是完整的
    let urlStr = props.documentUrl
    
    // 处理各种URL格式
    if (!urlStr.startsWith('http')) {
      // 如果是相对路径，转换为绝对路径
      if (!urlStr.startsWith('/')) {
        urlStr = `/${urlStr}`
      }
      
      // 添加域名
      urlStr = `${window.location.origin}${urlStr}`
    }
    
    const url = new URL(urlStr)
    
    // 添加格式和时间戳参数
    url.searchParams.set('format', 'html')
    url.searchParams.set('t', Date.now().toString())
    
    // 打印完整URL供调试
    const finalUrl = url.toString()
    console.log('[DocxPreview] 构建文档URL:', finalUrl)
    return finalUrl
  } catch (error) {
    console.error('[DocxPreview] URL构建错误:', error, '原始URL:', props.documentUrl)
    // 如果URL构建失败，返回原始URL
    return props.documentUrl
  }
})

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.documentId) {
    fetchHtml()
  }
})

// 监听对话框状态变化
watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal) {
    emit('close')
  } else if (props.documentId) {
    fetchHtml()
  }
})

// 拉取html内容并渲染
async function fetchHtml() {
  loading.value = true
  error.value = ''
  htmlContent.value = ''
  try {
    const resp = await fetch(`/api/templates/${props.documentId}/preview?format=html`)
    if (!resp.ok) throw new Error('获取文档失败')
    htmlContent.value = await resp.text()
  } catch (e) {
    error.value = (e as any).message || '加载失败'
    htmlContent.value = ''
  } finally {
    loading.value = false
  }
}
async function loadDocument() {
  console.log('[DocxPreview] 开始加载文档:', {
    documentUrl: props.documentUrl,
    documentId: props.documentId,
    htmlContent: props.htmlContent?.substring(0, 100) + '...'
  })
  
  if (!props.documentUrl && !props.documentId && !props.htmlContent) {
    console.warn('[DocxPreview] 没有可用的文档')
    error.value = '没有可用的文档'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    if (props.documentUrl && contentRef.value) {
      console.log('[DocxPreview] 准备显示文档URL:', documentUrl.value)
      
      // 使用我们正在运行的API端点获取HTML内容
      loading.value = true
      error.value = ''
      
      fetch(documentUrl.value)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP 错误! 状态码: ${response.status}`)
          }
          return response.text()
        })
        .then(html => {
          // 设置内容
          if (contentRef.value) {
            // 创建一个安全的容器来显示内容
            contentRef.value.innerHTML = `
              <div class="html-content" style="width:100%; height:100%; overflow:auto; padding:20px;">
                ${html}
              </div>
            `
          }
          
          loading.value = false
          emit('load', true)
        })
        .catch(err => {
          console.error('[DocxPreview] 加载文档失败:', err)
          error.value = `加载文档失败: ${err.message}`
          loading.value = false
          emit('error', error.value)
        })
    } else if (props.htmlContent && contentRef.value) {
      // 直接渲染HTML
      contentRef.value.innerHTML = props.htmlContent
      loading.value = false
      emit('load', true)
    } else {
      loading.value = false
      emit('load', true)
    }
  } catch (err) {
    console.error('加载文档失败:', err)
    error.value = err instanceof Error ? err.message : '加载文档失败'
    loading.value = false
    emit('error', error.value)
  }
}

// 处理对话框关闭
function handleDialogClose() {
  dialogVisible.value = false
  emit('close')
}

// 重新加载文档
function reload() {
  loadDocument()
}

// 对外暴露方法
defineExpose({
  reload
})

// 组件挂载后初始化
onMounted(() => {
  console.log('[DocxPreview] 组件挂载, autoLoad:', props.autoLoad, ' dialogMode:', props.dialogMode, ' documentUrl:', props.documentUrl)
  if (props.autoLoad && !props.dialogMode) {
    console.log('[DocxPreview] 自动加载文档')
    loadDocument()
  }
})
</script>

<style scoped>
.docx-preview {
  width: 100%;
}

.preview-container {
  width: 100%;
  overflow: auto;
}

.inline-preview {
  width: 100%;
  height: v-bind(height);
}

:deep(.content-container) {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: auto;
}

:deep(.loading-state),
:deep(.error-state),
:deep(.empty-state) {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

:deep(.content) {
  width: 100%;
  height: 100%;
  overflow: auto;
}

:deep(.empty-icon) {
  font-size: 48px;
  color: #909399;
}

:deep(.el-dialog__body) {
  padding: 16px;
}
</style>
