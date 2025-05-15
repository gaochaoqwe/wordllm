<template>
  <div class="ai-chat-box">
    <!-- 聊天消息区域 -->
    <div ref="messagesContainer" class="chat-messages">
      <!-- 系统欢迎消息 -->
      <div class="message system-message">
        <div class="message-content">
          <p>👋 您好！我是您的智能写作助手，可以帮您：</p>
          <ul>
            <li>生成章节内容</li>
            <li>优化文档段落</li>
            <li>回答写作相关问题</li>
            <li>提供内容建议</li>
          </ul>
          <p>请告诉我您需要什么帮助？</p>
        </div>
      </div>
      
      <!-- 动态消息列表 -->
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="['message', msg.role === 'user' ? 'user-message' : 'ai-message']"
      >
        <div class="message-avatar">
          <el-avatar :size="36" :icon="msg.role === 'user' ? UserFilled : Avatar" />
        </div>
        <!--
  v-html is used here to render formatted message content (with line breaks and code blocks).
  WARNING: Only use v-html with trusted content to avoid XSS vulnerabilities.
-->
<div class="message-content" v-html="formatMessage(msg.content)"></div>
      </div>
      
      <!-- 加载中提示 -->
      <div class="message ai-message" v-if="isLoading">
        <div class="message-avatar">
          <el-avatar :size="36" :icon="Avatar" />
        </div>
        <div class="message-content loading">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>
    
    <!-- 快捷操作按钮 -->
    <div class="quick-actions" v-if="chapter">
      <el-button 
        size="small" 
        type="primary" 
        plain 
        :disabled="isLoading"
        @click="generateChapterContent"
      >
        生成"{{ chapter.title }}"的内容
      </el-button>
      
      <el-button 
        size="small" 
        plain 
        :disabled="isLoading"
        @click="askPrompt('如何优化这部分内容？')"
      >
        优化内容
      </el-button>
      
      <el-button 
        size="small"
        plain
        :disabled="isLoading"
        @click="askPrompt('帮我扩展这部分内容')"
      >
        扩展内容
      </el-button>
    </div>
    
    <!-- 聊天输入框 -->
    <div class="chat-input">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="2"
        :placeholder="chapter ? '询问关于' + chapter.title + '的问题...' : '请先选择章节...'"
        :disabled="!chapter || isLoading"
        @keyup.enter.ctrl="sendMessage"
      />
      <el-button 
        type="primary" 
        :icon="Promotion" 
        circle 
        class="send-button"
        :disabled="!chapter || !userInput.trim() || isLoading"
        @click="sendMessage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'

import { UserFilled, Promotion } from '@element-plus/icons-vue'
import { Avatar } from "@element-plus/icons-vue";



// 类型定义
interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface Chapter {
  chapterNumber: string;
  title: string;
  content?: string;
}

// Props和事件
const props = defineProps<{
  chapter?: Chapter | null;
}>()

const emit = defineEmits<{
  (e: 'generate-content', content: string): void;
}>()

// 状态
const messages = ref<Message[]>([])
const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

// 当前上下文历史
let conversationHistory: Message[] = []

// 监听章节变化，清空聊天记录
watch(() => props.chapter, (newChapter) => {
  if (newChapter) {
    // 章节变更时重置聊天
    messages.value = [{
      role: 'assistant',
      content: `我已切换到"${newChapter.title}"章节。您想要为这个章节做什么？`
    }]
    
    // 重置上下文历史
    conversationHistory = [
      { role: 'system', content: `当前正在编辑的章节是"${newChapter.title}"，章节编号是${newChapter.chapterNumber}。` }
    ]
    
    // 清空输入框
    userInput.value = ''
  }
}, { immediate: true })

// 发送消息
function sendMessage() {
  if (!userInput.value.trim() || !props.chapter || isLoading.value) return
  
  // 添加用户消息
  const userMessage = { role: 'user' as const, content: userInput.value }
  messages.value.push(userMessage)
  conversationHistory.push(userMessage)
  
  // 清空输入
  const userQuery = userInput.value
  userInput.value = ''
  
  // 滚动到底部
  scrollToBottom()
  
  // 标记加载中
  isLoading.value = true
  
  // 模拟AI回答延迟
  setTimeout(() => {
    const aiResponse = simulateAiResponse(userQuery)
    
    // 添加AI回答
    const aiMessage = { role: 'assistant' as const, content: aiResponse }
    messages.value.push(aiMessage)
    conversationHistory.push(aiMessage)
    
    // 取消加载状态
    isLoading.value = false
    
    // 滚动到底部
    scrollToBottom()
  }, 1000 + Math.random() * 1000) // 随机1-2秒的延迟
}

// 模拟AI响应
function simulateAiResponse(query: string): string {
  // 根据当前章节和用户输入模拟响应
  const chapterTitle = props.chapter?.title || '未知章节'
  
  if (query.toLowerCase().includes('生成') || query.toLowerCase().includes('创建')) {
    return `好的，以下是我为"${chapterTitle}"生成的内容建议：\n\n${generateSampleContent(chapterTitle)}`
  }
  else if (query.toLowerCase().includes('优化') || query.toLowerCase().includes('改进')) {
    return `我可以帮您优化"${chapterTitle}"的内容。以下是一些建议：\n\n1. 增加具体案例和数据支持\n2. 使用更专业的行业术语\n3. 添加图表或可视化元素\n4. 确保逻辑结构清晰\n\n需要我针对某个具体方面提供详细优化建议吗？`
  }
  else if (query.toLowerCase().includes('扩展') || query.toLowerCase().includes('延伸')) {
    return `为"${chapterTitle}"扩展内容时，您可以考虑以下几个方向：\n\n1. 行业最佳实践分析\n2. 成功案例研究\n3. 潜在风险和应对策略\n4. 未来发展趋势\n\n您希望我针对哪个方向提供详细内容？`
  }
  else {
    return `关于"${chapterTitle}"的问题，我理解您想了解${query.slice(0, 15)}...相关的内容。\n\n我建议先明确本章节的核心目标，然后围绕这个目标展开讨论。请问您对这个章节有什么特定的要求或期望吗？`
  }
}

// 生成示例内容
function generateSampleContent(title: string): string {
  return `# ${title}\n\n## 概述\n\n本章节主要介绍关于${title}的核心概念、实施方法和评估标准。在现代软件开发中，${title}是确保项目成功的关键因素之一。\n\n## 主要内容\n\n1. ${title}的定义和重要性\n2. 实施${title}的最佳实践\n3. ${title}的评估标准和方法\n4. 案例分析与经验总结\n\n## 详细说明\n\n${title}作为软件开发领域的重要组成部分，需要团队成员的共同参与和理解。通过系统化的流程和方法，可以显著提升项目质量和效率。`
}

// 使用预设提示
function askPrompt(prompt: string) {
  userInput.value = prompt
  sendMessage()
}

// 生成章节内容
function generateChapterContent() {
  if (!props.chapter) return
  
  isLoading.value = true
  
  // 添加用户消息
  messages.value.push({ 
    role: 'user', 
    content: `请为"${props.chapter.title}"章节生成完整内容` 
  })
  
  // 滚动到底部
  scrollToBottom()
  
  // 模拟生成延迟
  setTimeout(() => {
    const content = generateSampleContent(props.chapter?.title || '')
    
    // 添加AI回答
    messages.value.push({ 
      role: 'assistant', 
      content: `我已为"${props.chapter?.title}"生成以下内容：\n\n${content}\n\n您可以点击"使用此内容"按钮将其添加到编辑器，或继续与我讨论修改建议。`,
    })
    
    // 发送事件通知父组件
    emit('generate-content', content)
    
    // 取消加载状态
    isLoading.value = false
    
    // 滚动到底部
    scrollToBottom()
  }, 2000)
}

// 格式化消息内容（处理换行等）
function formatMessage(content: string): string {
  return content
    .replace(/\n/g, '<br>')
    .replace(/```([^`]+)```/g, '<pre class="code-block">$1</pre>')
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 组件挂载后滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.ai-chat-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 90%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.ai-message, .system-message {
  align-self: flex-start;
}

.system-message {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 16px;
}

.system-message .message-content {
  font-size: 14px;
  color: #606266;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  background-color: #fff;
  padding: 12px;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  overflow-wrap: break-word;
}

.user-message .message-content {
  background-color: #409eff;
  color: white;
}

.ai-message .message-content, .system-message .message-content {
  background-color: #f5f7fa;
  color: #303133;
}

.message-content :deep(pre.code-block) {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  margin: 10px 0;
}

.quick-actions {
  display: flex;
  padding: 10px 16px;
  gap: 8px;
  flex-wrap: wrap;
  border-top: 1px solid #e6e6e6;
}

.chat-input {
  display: flex;
  padding: 16px;
  gap: 10px;
  border-top: 1px solid #e6e6e6;
}

.send-button {
  flex-shrink: 0;
  align-self: flex-end;
}

.loading {
  display: flex;
  gap: 5px;
  align-items: center;
  justify-content: center;
  min-height: 30px;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #909399;
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1.3s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
  } 
  40% { 
    transform: scale(1.0);
  }
}
</style>
