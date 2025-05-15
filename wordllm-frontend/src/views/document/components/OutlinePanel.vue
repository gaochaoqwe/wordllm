<template>
  <div class="outline-panel-container">
    <h2 class="panel-title">
      章节大纲
    </h2>
    <div v-if="!chapters || chapters.length === 0" class="no-chapters-tip">
      加载中...或未发现章节数据
    </div>
    <div v-else>
      <p class="debug-info">
        找到{{ chapters.length }}个章节
      </p>
      <ChapterOutlineTree 
        :chapters="chapters" 
        :chapter-statuses="chapterStatuses"
        @select-chapter="handleSelectChapter" 
      />
      
      <!-- 添加批量生成按钮 -->
      <div class="batch-actions">
        <el-button 
          type="primary" 
          size="small" 
          :disabled="autoGenerating"
          @click="autoGenerateAllContent"
        >
          一键生成所有章节内容
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDocumentEditor } from '../composables/useDocumentEditor'
import ChapterOutlineTree from './ChapterOutlineTree.vue'

// 从组合式函数获取共享状态和方法
const {
  chapters,
  chapterStatuses,
  autoGenerating,
  handleSelectChapter,
  autoGenerateAllContent
} = useDocumentEditor()
</script>

<style scoped>
.outline-panel-container {
  height: 100%;
  padding: 15px;
  overflow-y: auto;
  border-right: 1px solid #eee;
}

.panel-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.2rem;
  color: #333;
}

.no-chapters-tip {
  color: #999;
  font-style: italic;
  margin: 20px 0;
}

.debug-info {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 10px;
}

.batch-actions {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}
</style>
