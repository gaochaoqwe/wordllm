<template>
  <div class="chapter-tree">
    <div
      v-for="(chapter, index) in chapters"
      :key="chapter.id || index"
      class="chapter-item"
      :class="{
        'is-root': level === 0,
        'is-expanded': expandedNodes[chapter.id || index]
      }"
    >
      <div class="chapter-header">
        <div class="title-section">
          <span 
            v-if="chapter.children && chapter.children.length > 0"
            class="expand-icon" 
            @click="toggleNode(chapter.id || index)"
          >
            {{ expandedNodes[chapter.id || index] ? '▼' : '▶' }}
          </span>
          <span v-else class="empty-icon"></span>
          
          <span class="chapter-icon">
            <i v-if="level > 0" class="el-icon-document"></i>
            <i v-else class="el-icon-folder"></i>
          </span>
          
          <span 
            class="chapter-title" 
            @click="toggleNode(chapter.id || index)"
          >
            <template v-if="level === 0">* </template>{{ chapter.chapter_number || chapter.chapterNumber }}. {{ chapter.title }}
          </span>
        </div>
        
        <div class="action-section">
          <span v-if="chapter.requirement" class="status-indicator">
            <i class="el-icon-check" style="color: #67c23a;"></i>
          </span>
          <el-button 
            size="mini" 
            type="primary" 
            plain
            @click="emit('add-requirement', chapter)"
          >
            添加要求
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            plain
            @click="emit('remove-chapter', chapter)"
          >
            删除
          </el-button>
        </div>
      </div>
      
      <div 
        v-if="chapter.children && chapter.children.length > 0 && expandedNodes[chapter.id || index]" 
        class="subchapters"
      >
        <ChapterTree 
          :chapters="chapter.children" 
          :level="level + 1" 
          @add-requirement="emit('add-requirement', $event)" 
          @remove-chapter="emit('remove-chapter', $event)" 
        />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { watch, reactive } from 'vue'
import type { Chapter } from '../logic/types'



const props = defineProps<{ chapters: Chapter[], level?: number }>()
const chapters = props.chapters
const level = props.level ?? 0

// 跟踪节点展开状态的对象
const expandedNodes = reactive<Record<string | number, boolean>>({})

// 初始化：默认展开第一级节点
if (level === 0) {
  chapters.forEach((chapter, index) => {
    expandedNodes[chapter.id || index] = true
  })
}

// 切换节点展开/折叠状态
function toggleNode(nodeId: string | number) {
  expandedNodes[nodeId] = !expandedNodes[nodeId]
}

// Debug: log chapters prop when it changes
watch(() => chapters, (val) => {
  console.log('[DEBUG-CHAPTER-TREE] chapters prop:', val)
}, { immediate: true })

const emit = defineEmits(['add-requirement', 'remove-chapter'])

</script>

<!-- Ensure default export for SFC -->
<!-- This file uses <script setup>, which automatically provides a default export. No changes needed unless using classic API. -->
<style scoped>
.chapter-tree {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  width: 100%;
}

.chapter-item {
  position: relative;
  margin: 1px 0;
  padding: 2px 0;
  transition: all 0.2s;
}

.chapter-item.is-root {
  margin-bottom: 4px;
}

.chapter-item:hover {
  background-color: #f5f7fa;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 4px;
  min-height: 40px;
  border-radius: 4px;
  cursor: pointer;
}

.title-section {
  display: flex;
  align-items: center;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.expand-icon {
  cursor: pointer;
  width: 16px;
  display: inline-block;
  text-align: center;
  color: #409EFF;
  font-size: 12px;
  margin-right: 6px;
}

.empty-icon {
  width: 16px;
  display: inline-block;
  margin-right: 6px;
}

.chapter-icon {
  color: #606266;
  margin-right: 5px;
  font-size: 14px;
}

.chapter-title {
  font-size: 14px;
  color: #303133;
  font-weight: normal;
  cursor: pointer;
}

.is-root > .chapter-header .chapter-title {
  font-weight: 600;
  font-size: 15px;
  color: #409EFF;
}

.action-section {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.chapter-item:hover .action-section {
  opacity: 1;
}

.status-indicator {
  margin-right: 6px;
}

.subchapters {
  margin-left: 24px;
  padding-left: 12px;
  border-left: 1px dashed #dcdfe6;
}

/* 为子组件的子节点添加小缩进 */
:deep(.chapter-header) {
  padding-left: 8px;
}

/* 按钮样式优化 */
:deep(.el-button--mini) {
  padding: 5px 10px;
  font-size: 12px;
}

/* 悬停突出显示 */
.chapter-header:hover {
  background-color: #ecf5ff;
}
</style>
