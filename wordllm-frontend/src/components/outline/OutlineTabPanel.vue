<template>
  <div class="left-tab-panel">
    <!-- 顶部Tab按钮组 -->
    <div class="tab-buttons">
      <el-button 
        :type="activeTab === 'template' ? 'primary' : 'default'" 
        @click="$emit('update:activeTab', 'template')"
        class="tab-button"
      >依据模板</el-button>
      <el-button 
        :type="activeTab === 'input' ? 'primary' : 'default'" 
        @click="$emit('update:activeTab', 'input')"
        class="tab-button"
      >输入文件</el-button>
      <el-button 
        :type="activeTab === 'kb' ? 'primary' : 'default'" 
        @click="$emit('update:activeTab', 'kb')"
        class="tab-button"
      >知识库文件</el-button>
    </div>
    <!-- 预览内容区 -->
    <div class="tab-content">
      <!-- 模板预览 -->
      <div v-if="activeTab === 'template'" class="tab-pane">
        <DocxPreview v-if="templateId" :document-id="templateId" dialog-mode style="height: 420px" />
        <div v-else class="empty-preview">无模板可预览</div>
      </div>
      <!-- 输入文件预览 -->
      <div v-if="activeTab === 'input'" class="tab-pane">
        <DocxPreview v-if="inputFilePath" :file-path="inputFilePath" dialog-mode style="height: 420px" />
        <div v-else class="empty-preview">无输入文件可预览</div>
      </div>
      <!-- 知识库文件 -->
      <div v-if="activeTab === 'kb'" class="tab-pane">
        <div class="empty-preview">（此处可扩展上传/选择知识库文件功能）</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DocxPreview from '@/components/DocxPreview.vue'
import { defineProps } from 'vue'
const props = defineProps({
  activeTab: String,
  templateId: [String, Number],
  inputFilePath: String
})
</script>

<style scoped>
.left-tab-panel { width: 320px; }
.tab-buttons { display: flex; justify-content: space-between; margin-bottom: 12px; }
.tab-button { flex: 1; margin: 0 2px; }
.tab-content { background: #f7f7fa; border-radius: 8px; padding: 0 8px; }
.tab-pane { min-height: 420px; }
.empty-preview { color: #bbb; text-align: center; padding: 80px 0; }
</style>
