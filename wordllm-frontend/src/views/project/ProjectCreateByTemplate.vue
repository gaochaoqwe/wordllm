<template>
  <!-- 使用单一根元素包裹所有内容 -->
  <div>
    <div class="project-create-by-template">
      <el-card class="select-template-card">
        <div class="section-title">
          选择模板
        </div>
        <el-select 
          v-model="selectedTemplateId" 
          placeholder="请选择模板" 
          filterable 
          style="width: 300px" 
          :loading="loadingTemplates"
        >
          <el-option
            v-for="tpl in templates"
            :key="tpl.id"
            :label="tpl.title"
            :value="tpl.id"
          />
        </el-select>
      </el-card>
      
      <!-- 新增项目名称输入框 -->
      <el-card class="project-name-card">
        <div class="section-title">
          输入项目名称
        </div>
        <el-input 
          v-model="projectName" 
          placeholder="请输入项目名称" 
          style="width: 300px"
        />
      </el-card>

      <el-card class="upload-input-file-card">
        <div class="section-title">
          上传输入文件（如任务书等）
        </div>
        <FileUploader @file-selected="handleFileChange" />
        <div v-if="inputFileName" class="file-name">
          已选择文件: {{ inputFileName }}
        </div>
      </el-card>

      <div class="actions">
        <el-button 
          style="margin-right: 10px"
          type="info" 
          :disabled="!selectedTemplateId" 
          @click="showEditPromptDialog" 
        >
          修改目录生成提示词
        </el-button>
        <el-button 
          type="primary" 
          :disabled="!selectedTemplateId || !inputFile || !projectName.trim()" 
          @click="generateOutline"
        >
          一键生成目录大纲
        </el-button>
      </div>
    </div>
    

    
    <!-- 修改提示词对话框 -->
    <el-dialog
      v-model="showPromptDialog"
      title="修改目录生成提示词"
      width="60%"
      :close-on-click-modal="false"
    >
      <div v-if="loadingPrompt" class="prompt-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else>
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          <p>自定义提示词可以指导 AI 生成符合您需求的目录大纲。</p>
        </el-alert>
        <el-form :model="promptForm" label-position="top" style="margin-top: 15px">
          <el-form-item label="目录大纲生成提示词">
            <el-input
              v-model="promptForm.outlinePrompt"
              type="textarea"
              :rows="8"
              placeholder="请输入自定义提示词来指导 AI 生成目录大纲..."
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPromptDialog = false">取消</el-button>
          <el-button type="primary" :loading="savingPrompt" @click="savePrompt">保存</el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 大纲生成流式响应对话框 -->
    <el-dialog
      v-model="streamingDialog"
      title="正在生成大纲"
      width="70%"
      :close-on-click-modal="false"
      :close-on-press-escape="!isStreaming"
      :show-close="!isStreaming"
    >
      <div class="streaming-content">
        <div v-if="isStreaming" class="streaming-loading">
          <el-icon class="streaming-icon">
            <Loading />
          </el-icon>
          <span>模型正在生成大纲...</span>
        </div>
        <div v-else class="streaming-complete">
          <el-icon class="complete-icon">
            <Check />
          </el-icon>
          <span>内容生成完成！</span>
        </div>
        <div class="content-container">
          <pre class="model-output">{{ streamingContent }}</pre>
        </div>
      </div>
      <template #footer>
        <div class="streaming-footer">
          <el-button 
            v-if="!isStreaming" 
            type="primary" 
            @click="streamingDialog = false"
          >
            关闭
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Check } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import FileUploader from '../../components/FileUploader.vue'

import { createProject } from '../../api/project'
import { api } from '../../api/template' // 用于模板相关API
import request from '../../utils/request' // 用于直接调用API

const router = useRouter()
interface TemplateItem {
  id: number
  title: string
  outline_prompt?: string
  content?: string
  fileType?: string
  fileSize?: number
  status?: string
  created_at?: string
  updated_at?: string
}

const templates = ref<TemplateItem[]>([])
const loadingTemplates = ref(false)
const selectedTemplateId = ref<number | null>(null)
const inputFile = ref<File | null>(null)
const inputFileName = ref('')
const projectName = ref('')  // 添加项目名称状态变量

// 流式返回相关状态
const streamingContent = ref('')
const isStreaming = ref(false)
const streamingDialog = ref(false)



// 提示词相关状态
const showPromptDialog = ref(false)
const loadingPrompt = ref(false)
const savingPrompt = ref(false)
const promptForm = ref({
  outlinePrompt: ''
})

// 加载模板列表 - 与模板管理页面完全一致
async function fetchTemplates() {
  loadingTemplates.value = true
  try {
    const response = await api.searchTemplates({
      title: '',
      page: 0,  // 不分页，请求第一页
      size: 1000 // 足够大的页面大小以获取所有模板
    })
    
    console.log('服务器返回的模板数据:', response)
    templates.value = response.content || []
    if (!Array.isArray(templates.value)) {
      console.warn('模板数据不是数组格式', response)
      templates.value = []
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
    ElMessage.error('加载模板失败')
  } finally {
    loadingTemplates.value = false
  }
}

function handleFileChange(file: File) {
  inputFile.value = file
  inputFileName.value = file.name
}

async function generateOutline() {
  // 添加项目名称检查
  if (!selectedTemplateId.value || !inputFile.value || !projectName.value.trim()) {
    ElMessage.warning('请选择模板、输入项目名称并上传输入文件')
    return
  }

  // 重置流式内容状态
  streamingContent.value = ''
  streamingDialog.value = true
  isStreaming.value = true
  
  interface ProjectData {
    success: boolean
    data?: {
      id: number
      title?: string
    }
    message?: string
  }

  let projectData: ProjectData;
  try {
    // 1. 先创建项目
    // 获取模板名称
    const tpl = templates.value.find((t: TemplateItem) => t.id === selectedTemplateId.value)
    const templateName = tpl?.title || '无名模板'
    
    console.log(`[测试] 创建项目 - 项目名称: ${projectName.value}, 模板名称: ${templateName}`)
    
    // 使用新的API结构创建项目
    const projectRes = await createProject({
      project_name: projectName.value,        // 使用用户输入的项目名称
      template_name: templateName,            // 使用选中模板的模板名称
      templateId: selectedTemplateId.value,   // 关联的模板ID
      inputFile: inputFile.value.name         // 输入文件名称
    })
    projectData = projectRes as ProjectData
    if (!projectData.success || !projectData.data || !projectData.data.id) {
      throw new Error('创建项目失败')
    }
    // 2. 获取模板提示词信息
    console.log(`[测试-生成大纲] 获取模板ID: ${selectedTemplateId.value} 的提示词`)
    let templatePrompt = ''
    try {
      const templateRes = await fetch(`/api/templates/${selectedTemplateId.value}`)
      const templateData = await templateRes.json()
      
      if (templateData && templateData.outline_prompt) {
        templatePrompt = templateData.outline_prompt
        console.log(`[测试-生成大纲] 成功获取模板提示词: ${templatePrompt}`)
      } else {
        console.log(`[测试-生成大纲] 模板没有提示词或获取失败`)
      }
    } catch (error) {
      console.error(`[测试-生成大纲] 获取模板提示词出错:`, error)
    }
    
    // 3. 准备表单数据
    const formData = new FormData()
    formData.append('template_id', String(selectedTemplateId.value))
    formData.append('input_file', inputFile.value)
    // 确保project_id转换为字符串
    formData.append('project_id', String(projectData.data.id))
    
    // 添加模板提示词（如果有）
    if (templatePrompt) {
      formData.append('outline_prompt', templatePrompt)
      console.log(`[测试-生成大纲] 已添加提示词到请求中`)
    }
    
    // 发送流式请求获取大纲
    console.log(`[测试-生成大纲] 发送流式大纲生成请求`)
    const response = await fetch('/api/outlines/generate-streaming', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status} ${response.statusText}`)
    }
    
    // 创建一个Reader来读取流
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法创建响应流读取器')
    }
    
    // 用于保存完整的响应文本
    let completeResponse = ''
    
    // 读取流
    let streamingDone = false
    while (!streamingDone) {
      const { done, value } = await reader.read()
      
      if (done) {
        console.log('Stream complete')
        streamingDone = true
        continue
      }
      
      // 将二进制数据转换为文本
      const chunk = new TextDecoder().decode(value)
      completeResponse += chunk
      
      try {
        // 尝试解析当前收到的数据
        // 注意：流式响应的JSON可能不完整，这里要处理这种情况
        const partialResponse = JSON.parse(completeResponse)
        
        if (partialResponse.streaming && partialResponse.content) {
          // 更新界面上显示的内容
          streamingContent.value = partialResponse.content
        }
        
        // 如果解析成功且流结束，检查是否完成
        if (partialResponse.parsed === true) {
          console.log('流式内容接收完成，模型输出解析成功')
          isStreaming.value = false
          
          // 当内容生成完成后，跳转到结果页面
          setTimeout(() => {
            streamingDialog.value = false
            router.push({
              path: '/document/outline-result',
              query: {
                projectId: projectData.data.id,
                templateId: partialResponse.template?.id || '',
                inputFileName: inputFile.value.name || '',
              }
            })
          }, 1000) // 给用户一秒钟时间看结果
        }
      } catch (e) {
        // JSON解析错误，可能是因为数据还不完整，继续等待更多数据
        console.log('流式数据尚未完成，继续接收...')
      }
    }
  } catch (error) {
    console.error('生成大纲失败:', error)
    ElMessage.error(`生成大纲失败: ${error.message || '未知错误'}`)
    isStreaming.value = false
    // 如果出错，允许用户关闭对话框
    setTimeout(() => {
      streamingDialog.value = false 
    }, 2000)
  }
}

// 显示编辑提示词对话框
async function showEditPromptDialog() {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择模板')
    return
  }
  
  showPromptDialog.value = true
  loadingPrompt.value = true
  
  try {
    // 直接使用选中的模板
    const selectedTemplate = templates.value.find(t => t.id === selectedTemplateId.value)
    
    if (selectedTemplate) {
      console.log('从本地数据中获取的模板:', selectedTemplate)
      
      // 输出所有属性名称，帮助调试
      console.log('模板对象的所有属性:')
      for (const key in selectedTemplate) {
        console.log(`- ${key}: ${typeof selectedTemplate[key]}`, selectedTemplate[key])
      }
      
      // 设置提示词，只使用outline_prompt属性
      promptForm.value.outlinePrompt = selectedTemplate.outline_prompt || ''
    } else {
      // 如果在本地数据中找不到，尝试从后端获取
      console.log('在本地数据中未找到模板，尝试从后端获取...')
      const response = await request.get(`/api/templates/${selectedTemplateId.value}`)
      console.log('从后端获取的模板数据:', response)
      
      if (response && response.data) {
        const template = response.data
        // 输出响应对象的属性
        console.log('响应数据的所有属性:')
        for (const key in template) {
          console.log(`- ${key}: ${typeof template[key]}`, template[key])
        }
        
        // 尝试不同的路径获取模板的outline_prompt
        if (template.outline_prompt) {
          promptForm.value.outlinePrompt = template.outline_prompt
        } else if (template.content_prompt) { // 根据截图中的情况尝试使用content_prompt
          promptForm.value.outlinePrompt = template.content_prompt
          console.log('使用content_prompt替代:', template.content_prompt)
        } else {
          // 检查data字段
          if (template.data && template.data.outline_prompt) {
            promptForm.value.outlinePrompt = template.data.outline_prompt
            console.log('从嵌套data字段找到outline_prompt:', template.data.outline_prompt)
          } else {
            promptForm.value.outlinePrompt = ''
          }
        }
      }
    }
  } catch (error) {
    console.error('获取提示词失败:', error)
    ElMessage.error('获取提示词失败')
  } finally {
    loadingPrompt.value = false
  }
}

// 保存提示词
async function savePrompt() {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择模板')
    return
  }
  
  savingPrompt.value = true
  
  try {
    // 直接使用fetch发送请求，绕过封装的API
    // 关键不同点: 使用JSON格式而非FormData
    const requestData = { outline_prompt: promptForm.value.outlinePrompt }
    
    console.log('发送的提示词数据:', promptForm.value.outlinePrompt)
    console.log('发送的JSON数据:', requestData)
    
    const response = await fetch(`/api/templates/${selectedTemplateId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    })
    
    const result = await response.json()
    console.log('更新提示词响应:', result)
    
    // 判断响应是否成功
    if (response.ok) {
      // 更新当前的templates数组中的对应模板
      const index = templates.value.findIndex(t => t.id === selectedTemplateId.value)
      if (index !== -1) {
        templates.value[index].outline_prompt = promptForm.value.outlinePrompt
      }
      
      ElMessage.success('提示词更新成功')
      showPromptDialog.value = false
    } else {
      throw new Error(result.message || '更新提示词失败')
    }
  } catch (error) {
    console.error('更新提示词失败:', error)
    ElMessage.error('更新提示词失败')
  } finally {
    savingPrompt.value = false
  }
}

onMounted(fetchTemplates)
</script>

<style scoped>
.project-create-by-template {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}
.select-template-card, .upload-input-file-card {
  margin-bottom: 24px;
}
.section-title {
  font-weight: bold;
  margin-bottom: 12px;
}
.file-name {
  margin-top: 8px;
  color: #888;
}
.actions {
  text-align: center;
  margin-top: 32px;
}
.prompt-loading {
  padding: 20px;
}

/* 流式内容显示样式 */
.streaming-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.streaming-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #409eff;
}

.streaming-icon {
  animation: rotate 1.5s linear infinite;
}

.streaming-complete {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #67c23a;
}

.content-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 15px;
  background-color: #f9f9f9;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.model-output {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  line-height: 1.5;
  margin: 0;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
