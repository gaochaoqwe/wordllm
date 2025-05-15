<template>
  <div class="content-editor-container">
    <div class="content-header">
      <h2 v-if="currentChapter">
        {{ currentChapter.title }}
      </h2>
      <h2 v-else>
        Document Content
      </h2>
      <div class="actions">
        <el-button
          size="small"
          type="primary"
          :disabled="!currentChapter"
          @click="saveContent"
        >
          保存
        </el-button>
        <el-button
          size="small"
          :disabled="!currentChapter || isGenerating"
          @click="generateContent"
        >
          {{ isGenerating ? '重新生成中...' : '不满意？重新生成' }}
        </el-button>
      </div>
    </div>
    <div class="content-editor">
      <el-input
        v-model="chapterContent"
        type="textarea"
        :rows="20"
        placeholder="Select a chapter from the left panel to start editing or use AI to generate content"
        :disabled="!currentChapter"
      />
    </div>
    
    <!-- Progress indicator for auto-generation -->
    <div v-if="autoGenerating" class="generation-progress">
      <p>Auto-generating all chapters: {{ currentGeneratingIndex + 1 }}/{{ chapters.length }}</p>
      <el-progress :percentage="generationProgress" />
    </div>
  </div>
</template>

<script setup lang="ts">
console.log('!!! ContentEditor.vue loaded !!!')
import { watch } from 'vue'
import { useDocumentEditor } from './composables/useDocumentEditor'



// Get shared state and methods from composable
const {
  chapters,
  currentChapter,
  chapterContent,
  isGenerating,
  autoGenerating,
  currentGeneratingIndex,
  generationProgress,
  saveContent,
  generateContent
} = useDocumentEditor()

// 调试：监听 currentChapter 的变化
watch(() => currentChapter.value, (val) => {
  console.log('[ContentEditor] currentChapter.value changed:', val)
  if (val) {
    console.log('[ContentEditor] currentChapter fields:', JSON.stringify(val))
    if (!val.chapterNumber) {
      console.warn('[ContentEditor] 当前章节缺少 chapterNumber 字段！', val)
    }
  }
})

// 调试：按钮禁用原因
watch([
  () => currentChapter.value,
  () => isGenerating.value
], ([chapter, generating]) => {
  console.log('[按钮状态] currentChapter:', chapter, 'isGenerating:', generating)
  console.log('[ContentEditor] currentChapter ref:', currentChapter)
  console.log('[ContentEditor] currentChapter value:', currentChapter.value)
  if (!chapter) {
    console.log('[按钮禁用] 未选择章节')
  }
  if (generating) {
    console.log('[按钮禁用] 正在生成内容')
  }
})
</script>

<style scoped>
.content-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 15px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.content-editor {
  flex-grow: 1;
  margin-top: 15px;
  margin-bottom: 15px;
}

.actions {
  display: flex;
  gap: 10px;
}

.generation-progress {
  margin-top: 15px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}
</style>
