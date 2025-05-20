<template>
  <div class="document-editor-container">
    <!-- 三栏布局：左侧大纲、中间内容、右侧AI聊天 -->
    <div class="editor-layout">
      <!-- 左侧大纲 -->
      <OutlinePanel class="outline-panel" />
      
      <!-- 中间内容编辑区 -->
      <ContentEditor class="content-panel" />
      
      <!-- 右侧AI聊天对话框 -->
      <div class="ai-chat-panel">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 class="panel-title">
            AI助手
          </h2>
          <el-button
            size="small"
            type="success"
            @click="showDownloadOptions = true"
          >
            下载全文
          </el-button>
        </div>
        <AiChatBox 
          :chapter="currentChapter" 
          @generate-content="handleGenerateContent"
        />
      </div>
    </div>
    <el-dialog
      v-model="showDownloadOptions"
      title="下载全文设置"
      width="900px"
      top="5vh"
      destroy-on-close
    >
      <DownloadDocxOptions @cancel="showDownloadOptions = false" @confirm="showDownloadOptions = false" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import { useDocumentEditor } from './composables/useDocumentEditor'
import ContentEditor from './ContentEditor.vue'
import OutlinePanel from './components/OutlinePanel.vue'
import AiChatBox from './components/AiChatBox.vue'
import DownloadDocxOptions from './downloadDocx/DownloadDocxOptions.vue'

const showDownloadOptions = ref(false)

// 使用组合式API获取共享状态和方法
const documentEditor = useDocumentEditor()
const { currentChapter, handleGenerateContent } = documentEditor

// 将文档编辑器状态和方法提供给子组件
provide('documentEditor', documentEditor)
</script>

<style scoped>
.document-editor-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.outline-panel {
  width: 250px;
  flex-shrink: 0;
  background-color: #f8f9fa;
}

.content-panel {
  flex: 1;
  overflow: auto;
  background-color: #fff;
}

.ai-chat-panel {
  width: 300px;
  flex-shrink: 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-left: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.panel-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.2rem;
  color: #333;
}

@media (max-width: 1200px) {
  .editor-layout {
    flex-direction: column;
  }
  
  .outline-panel, .content-panel, .ai-chat-panel {
    width: 100%;
    height: auto;
  }
  
  .outline-panel {
    height: 30vh;
  }
  
  .content-panel {
    flex: 1;
  }
  
  .ai-chat-panel {
    height: 30vh;
    border-left: none;
    border-top: 1px solid #eee;
  }
}
</style>
