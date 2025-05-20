<template>
  <div class="download-docx-options">
    <div class="download-title">
      <span>下载格式（当前总计{{ totalWords }}字）</span>
    </div>
    
    <div class="download-content">
      <!-- 左侧设置 -->
      <div class="left-settings">
        <!-- 标号样式 -->
        <SectionNumberStyle />
        <!-- 模板样式 -->
        <TemplateStyle />
      </div>
      
      <!-- 右侧设置 -->
      <div class="right-settings">
        <!-- 页面格式 -->
        <PageFormat />
        <!-- 一级标题样式 -->
        <TitleLevelStyle :level="1" />
        <!-- 二级标题样式 -->
        <TitleLevelStyle :level="2" />
        <!-- 三级标题样式 -->
        <TitleLevelStyle :level="3" />
        <!-- 正文格式 -->
        <TextStyle />
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="actions">
      <el-button
        @click="handleCancel"
      >
        取消
      </el-button>
      <el-button
        type="primary"
        @click="handleConfirm"
      >
        确定
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onCancel, onConfirm } from './DownloadDocxOptions.ts'
import SectionNumberStyle from './components/SectionNumberStyle.vue'
import TemplateStyle from './components/TemplateStyle.vue'
import PageFormat from './components/PageFormat.vue'
import TitleLevelStyle from './components/TitleLevelStyle.vue'
import TextStyle from './components/TextStyle.vue'

// 当前文档总字数
const totalWords = ref(2012)

// 定义要发出的事件
const emits = defineEmits(['cancel', 'confirm'])

// 修改处理函数调用 emits
function handleCancel() {
  onCancel() // 调用原来的函数（记录日志等）
  emits('cancel') // 触发父组件监听的事件
}

import { useRoute } from 'vue-router'
const route = useRoute()

async function handleConfirm() {
  // 获取projectId和chapterNumber
  const projectIdRaw = route.query.projectId || route.params.projectId
  const chapterNumberRaw = route.query.chapterNumber || route.params.chapterNumber
  const projectId = projectIdRaw && !Array.isArray(projectIdRaw) ? parseInt(projectIdRaw as string, 10) : undefined
  const chapterNumber = chapterNumberRaw && !Array.isArray(chapterNumberRaw) ? parseInt(chapterNumberRaw as string, 10) : undefined
  try {
    const result = await onConfirm(projectId, chapterNumber)
    if (result) {
      emits('confirm')
    }
  } catch (error) {
    console.error('确认下载时发生错误:', error)
  }
}
</script>

<style scoped>
.download-docx-options {
  padding: 20px;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.download-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
}

.download-content {
  display: flex;
  gap: 40px;
}

.left-settings {
  flex: 1;
  border-right: 1px solid #eee;
  padding-right: 20px;
}

.right-settings {
  flex: 1;
}

.actions {
  margin-top: 32px;
  text-align: right;
  border-top: 1px solid #eee;
  padding-top: 16px;
}
</style>
