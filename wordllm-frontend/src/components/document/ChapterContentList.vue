<template>
  <div class="chapter-content-list">
    <ChapterContentItem v-for="(chapter, idx) in chaptersData" :key="chapter.chapterNumber || idx" :chapter="chapter" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ChapterContentItem from './ChapterContentItem.vue'
const props = defineProps({
  chapterContents: { type: Array, default: () => [] },
  'chapter-contents': { type: Array, default: () => [] }
})

// 使用计算属性合并两种命名方式的输入
const chaptersData = computed(() => props.chapterContents || props['chapter-contents'] || [])
</script>

<style scoped>
.chapter-content-list { margin-top: 12px; }
</style>
