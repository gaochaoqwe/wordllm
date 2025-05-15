<template>
  <div class="chapter-content-list">
    <ChapterContentItem v-for="(chapter, idx) in chapterContents" :key="chapter.chapterNumber || idx" :chapter="chapter" />
  </div>
</template>

<script setup lang="ts">
import ChapterContentItem from './ChapterContentItem.vue'
const props = defineProps({
  chapterContents: { type: Array, required: true }
})
</script>

<style scoped>
.chapter-content-list { margin-top: 12px; }
</style>
