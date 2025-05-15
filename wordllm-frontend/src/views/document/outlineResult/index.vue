<template>
  <div class="outline-result-page">
    <div v-if="errorMsg" class="error-message">
      {{ errorMsg }}
    </div>

    <div v-else class="outline-result-layout">
      <!-- Left Panel for Tabs/Previews -->
      <div class="left-panel">
        <div class="tab-buttons">
          <div 
            class="tab-button" 
            :class="{active: outlineState.activeTab === 'template'}"
            @click="outlineState.activeTab = 'template'"
          >
            模板预览
          </div>
          <div 
            class="tab-button" 
            :class="{active: outlineState.activeTab === 'input'}"
            @click="outlineState.activeTab = 'input'"
          >
            输入文件
          </div>
        </div>
        <div class="tab-content">
          <div v-if="outlineState.activeTab === 'template'">
            <h4>{{ outlineState.templateTitle }}</h4>
            <!-- Placeholder for template preview content -->
            <p>模板预览内容区域</p>
            <el-button 
              v-if="outlineState.templatePath" 
              @click="previewState.previewVisible = true; previewState.previewTitle = outlineState.templateTitle; previewState.previewFilePath = outlineState.templatePath;"
            >
              查看模板文件
            </el-button>
          </div>
          <div v-else-if="outlineState.activeTab === 'input'">
            <h4>{{ outlineState.inputFileName }}</h4>
            <!-- Placeholder for input file preview content -->
            <p>输入文件内容区域</p>
            <el-button 
              v-if="outlineState.inputFilePath" 
              @click="previewState.previewVisible = true; previewState.previewTitle = outlineState.inputFileName; previewState.previewFilePath = outlineState.inputFilePath;"
            >
              查看输入文件
            </el-button>
          </div>
        </div>
      </div>

      <!-- Right Panel for Chapter Outline -->
      <div class="right-panel">
        <div class="outline-header">
          <span class="outline-title">章节目录</span>
          <el-switch v-model="outlineState.allChecked" active-text="一键校准全审" style="margin-left: 18px;" />
        </div>

        <div v-if="outlineState.chapters && outlineState.chapters.length > 0" class="outline-tree-container">
          <ChapterTree
            :chapters="outlineState.chapters"
            @add-requirement="addRequirementByNode"
            @remove-chapter="removeChapterByNode"
          />
        </div>
        <div v-else class="empty-state-container">
          <el-empty description="暂无章节数据，请尝试生成或添加章节。" :image-size="120">
            <template #description>
              <p>未找到章节目录数据，请尝试继续生成。</p>
            </template>
          </el-empty>
        </div>

        <div class="footer-actions">
          <el-button 
            type="primary" 
            @click="addChapter"
          >
            + 添加章节
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!outlineState.chapters || outlineState.chapters.length === 0"
            @click="showPromptDialog = true"
          >
            不满意？重生成大纲
          </el-button>
          <el-button 
            type="success" 
            :disabled="!outlineState.chapters || outlineState.chapters.length === 0"
            @click="navigateToContentEditor"
          >
            开始编辑正文内容
          </el-button>
        </div>
      </div>
    </div>

    <!-- Dialogs -->
    <PreviewPanel 
      v-model="previewState.previewVisible.value" 
      :title="previewState.previewTitle.value" 
      :file-path="previewState.previewFilePath.value" 
    />
    <RegeneratePromptDialog
      v-model="showPromptDialog.value"
      :init-prompt="outlinePrompt.value"
      @confirm="onPromptConfirm"
    />
    <RegenerateRequirementDialog 
      v-model="regenerateState.isRegenerating.value" 
      :default-requirement="regenerateState.regenerateRequirement.value" 
      @confirm="handleRegenerateConfirm" 
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import ChapterTree from './components/ChapterTree.vue'
import RegeneratePromptDialog from './components/RegeneratePromptDialog.vue'
import RegenerateRequirementDialog from './components/RegenerateRequirementDialog.vue'
import PreviewPanel from './components/PreviewPanel.vue'

// 导入逻辑
import {
  outlineState,
  previewState,
  regenerateState,
  initializeFromRoute,
  fetchTemplateDetails,
  fetchChapters,
  loadDefaultChapters,
  addChapter,
  /* eslint-disable-next-line no-unused-vars */
  removeChapterByNode,
  /* eslint-disable-next-line no-unused-vars */
  addRequirementByNode,
  regenerate,
  regenerateChapters,
  generateDocumentContent
} from './logic'

export default defineComponent({
  name: 'OutlineResultPage',
  components: {
    PreviewPanel,
    RegenerateRequirementDialog,
    RegeneratePromptDialog,
    ChapterTree
  },
  props: {
    projectId: {
      type: [String, Number],
      default: null
    },
    templateId: {
      type: Number,
      default: null
    },
    inputFileName: {
      type: String,
      default: ''
    }
  },
  setup() {
    // 错误信息用于显示到页面
    const errorMsg = ref('')
    const router = useRouter()
    const route = useRoute()
    // 重新生成目录弹窗控制与内容
    const showPromptDialog = ref(false)
    const outlinePrompt = ref('')

    // 获取 outline_prompt
    async function fetchOutlinePrompt() {
      // 假设后端接口 /api/templates/:templateId/prompts 返回 { outline_prompt: string, ... }
      if (!outlineState.templateId) return
      try {
        const res = await fetch(`/api/templates/${outlineState.templateId}/prompts`)
        const data = await res.json()
        outlinePrompt.value = data.outline_prompt || ''
      } catch (e) {
        outlinePrompt.value = ''
      }
    }

    // 保存 outline_prompt 并重新生成章节目录
    async function onPromptConfirm(newPrompt) {
      console.log(`[测试-A] 开始执行 onPromptConfirm, 接收到提示词: ${newPrompt}`)
      console.log(`[测试-A] 模板ID是: ${outlineState.templateId}`)
      
      // 立即设置值
      outlinePrompt.value = newPrompt
      
      // 准备请求数据
      const requestData = { outline_prompt: newPrompt }
      console.log(`[测试-A] 请求数据已准备:`, requestData)
      console.log(`[测试-A] JSON化后:`, JSON.stringify(requestData))
      
      // 使用正确的接口: PUT /api/templates/:templateId
      try {
        // 构建请求URL
        const requestUrl = `/api/templates/${outlineState.templateId}`
        console.log(`[测试-A] 将发送请求到: ${requestUrl}`)
        
        // 发送请求
        const response = await fetch(requestUrl, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        })
        
        console.log(`[测试-A] 请求状态: ${response.status} ${response.statusText}`)
        
        if (!response.ok) {
          throw new Error(`保存失败: ${response.status}`)
        }
        
        const result = await response.json()
        console.log(`[测试-A] 保存成功, 返回数据:`, result)
        console.log(`[测试-A] 返回数据中的outline_prompt: ${result.outline_prompt}`)
        
        ElMessage.success('提示词已保存')
      } catch (error) {
        console.error(`[测试-A] 保存出错:`, error)
        ElMessage.error(`保存失败: ${error.message}`)
      }
      
      // 重新生成章节目录
      await regenerate()
      await fetchOutlinePrompt()
    }

    // 页面初始化
    onMounted(async () => {
      // 确保对话框不会在页面加载时显示
      regenerateState.isRegenerating.value = false

      try {
        // 从路由参数初始化数据
        const route = useRoute()
        console.log('[DEBUG-INDEX] 当前route对象:', route.query)
        // 首先调用 initializeFromRoute 来填充 outlineState.templateId
        // initializeFromRoute directly modifies outlineState
        await initializeFromRoute(route)

        // 只有当 outlineState.templateId 有值时才获取 prompt
        if (outlineState.templateId) {
          await fetchOutlinePrompt();
        } else {
          console.warn('[DEBUG-INDEX] outlineState.templateId is null after initialization, skipping fetchOutlinePrompt.');
          // 可选：如果需要，设置一个默认的 outlinePrompt 或进行其他处理
          // outlinePrompt.value = ''; 
        }
        
        // 获取模板详情
        if (outlineState.templateId) {
          const templateData = await fetchTemplateDetails(outlineState.templateId)
          if (templateData) {
            console.log('[DEBUG-10] 模板详情获取成功:', templateData)
            // 注意: Vue 3中更新响应式对象的正确方式
            outlineState.templateTitle = templateData.title || '未命名模板'
            outlineState.templatePath = templateData.docx_path || ''
          }
        }
        
        // 获取章节数据
        try {
          const chapters = await fetchChapters(outlineState.projectId)
          console.log('[DEBUG-18] 获取到的章节数据:', chapters)
          console.log('[DEBUG-19] 章节数据类型:', typeof chapters, Array.isArray(chapters))
          
          if (chapters && chapters.length > 0) {
            if (Array.isArray(chapters)) {
              const mappedChapters = chapters.map((chapter) => {
                return {
                  chapterNumber: chapter.chapterNumber || chapter.chapter_number || '',
                  title: chapter.title || '',
                  children: chapter.children || [],
                  // 保留其他属性
                  ...chapter
                }
              })
              
              // 使用正确的响应式赋值方式
              outlineState.chapters = mappedChapters
              console.log('[DEBUG-20] 映射后的章节数据:', outlineState.chapters)
              console.log('[DEBUG-21] 首个章节示例:', outlineState.chapters[0])
            }
          } else {
            console.log('[DEBUG-22] 未获取到章节数据，使用默认章节')
            ElMessage.warning('未获取到章节目录，将使用默认数据')
            loadDefaultChapters()
            console.log('[DEBUG-23] 默认章节已加载:', outlineState.chapters)
          }
        } catch (error) {
          ElMessage.error('加载章节目录失败')
          loadDefaultChapters()
        }
      } catch (error) {
        ElMessage.error(error instanceof Error ? error.message : '页面初始化失败')
        errorMsg.value = error instanceof Error ? error.message : '页面初始化失败'
        // 不再自动跳转，留在本页显示错误
      }
    })
    
    // 确认重新生成
    function handleRegenerateConfirm(requirement: string) {
      regenerateState.regenerateRequirement.value = requirement
      regenerateChapters()
    }
    
    // 处理子章节重新生成
    function handleRegenerateSubchapters() {
      ElMessageBox.confirm(
        '确定要重新生成子章节吗？这将覆盖当前的子章节内容。', 
        '重新生成子章节', 
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 调用子章节重新生成逻辑
        ElMessage.info('子章节重新生成功能正在开发中')
      }).catch(() => {})
    }
    
    // 直接跳转到内容编辑页面
    function navigateToContentEditor() {
      if (!outlineState.chapters || outlineState.chapters.length === 0) {
        ElMessage.error('无可用的章节数据')
        return
      }
      
      // 获取当前项目ID
      const projectId = outlineState.projectId || route.query.projectId
      
      if (!projectId) {
        ElMessage.error('缺少项目ID，无法跳转到编辑页面')
        return
      }
      
      ElMessage.success('正在跳转到内容编辑页面')
      router.push({ path: '/document/editor', query: { projectId } })
    }
    
    // 处理生成文档 (保留原有函数)
    async function handleGenerateDocument() {
      if (!outlineState.chapters || outlineState.chapters.length === 0) {
        ElMessage.error('无可用的章节数据')
        return
      }
      
      outlineState.isGeneratingDocument = true
      
      // 显示加载指示器
      const loading = ElLoading.service({
        lock: true,
        text: '正在生成文档内容...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      try {
        const result = await generateDocumentContent()
        
        if (result.success) {
          ElMessage.success('已启动文档内容生成，正在跳转到编辑页面')
          router.push({ path: '/document/editor', query: { projectId: result.projectId } })
        }
      } catch (error) {
        console.error('生成文档内容错误:', error)
        ElMessage.error(`生成文档内容失败: ${error instanceof Error ? error.message : '未知错误'}`)
      } finally {
        // 关闭加载指示器
        loading.close()
        outlineState.isGeneratingDocument = false
      }
    }
    
    // 下载 DOCX 和 PDF 函数
    function downloadDocx() {
      ElMessage.info('下载DOCX功能正在开发中')
    }
    
    function downloadPdf() {
      ElMessage.info('下载PDF功能正在开发中')
    }
    
    // 添加需求节点
    // 已移除未使用的 addRequirementByNode 和 removeChapterByNode 以修复 lint 错误
    watch(() => regenerateState.isRegenerating.value, (newValue, oldValue) => {
      console.log(`[WATCHER] regenerateState.isRegenerating changed from ${oldValue} to ${newValue}`);
      if (newValue === true) {
        console.log('[WATCHER] regenerateState.isRegenerating became true. Stack trace attempt:');
        try {
          throw new Error('Stack trace for isRegenerating === true');
        } catch (e: unknown) {
          if (e instanceof Error) {
            console.error(e.stack);
          } else {
            console.error('An unknown error occurred for stack trace attempt:', e);
          }
        }
        // debugger; // Pause execution to inspect the call stack // Commented out
      }
    });

    return {
      // 状态
      outlineState,
      previewState,
      regenerateState,
      errorMsg,
      // 对话框控制
      showPromptDialog,
      outlinePrompt,
      onPromptConfirm,
      // 方法
      addChapter,
      removeChapterByNode,
      addRequirementByNode,
      navigateToContentEditor,
      handleGenerateDocument,
      // 函数
      regenerate,  // 添加到返回对象中以供模板使用
      handleRegenerateConfirm,
      handleRegenerateSubchapters,
      downloadDocx,
      downloadPdf
    }
  }
})
</script>

<style scoped>
.outline-result-page {
  min-height: 100vh;
  background: #f6f7fa;
  padding: 20px;
  box-sizing: border-box;
}

.error-message {
  color: red;
  text-align: center;
  padding: 20px;
  font-size: 1.2em;
}

.outline-result-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 40px); /* Adjust based on padding */
}

.left-panel {
  flex: 1;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow-y: auto;
}

.right-panel {
  flex: 2;
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.tab-buttons {
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.tab-button {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab-button.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-content h4 {
  margin-top: 0;
}

.outline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.outline-title {
  font-size: 1.1em;
  font-weight: bold;
}

.outline-tree-container {
  flex-grow: 1;
  overflow-y: auto; /* Allow tree to scroll if it's too long */
}

.empty-state-container {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  justify-content: flex-start;
}
</style>
