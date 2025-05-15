<template>
  <div class="chapter-content-item">
    <div class="chapter-title">
      <img :src="statusIcon" class="chapter-status-icon" :alt="chapter.status" />
      {{ chapter.chapterNumber }} {{ chapter.title }}
    </div>
    <div class="chapter-body" v-html="chapter.content || '<span style=\'color:#bbb\'>内容待生成</span>'"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  chapter: { type: Object, required: true }
})

const statusIcon = computed(() => {
  if (!props.chapter.status) return require('@/assets/chapter-status/pending.png')
  switch (props.chapter.status) {
    case 'generating':
      return require('@/assets/chapter-status/generating.gif')
    case 'done':
      return require('@/assets/chapter-status/done.png')
    case 'error':
      return require('@/assets/chapter-status/error.png')
    default:
      return require('@/assets/chapter-status/pending.png')
  }
})
</script>

<style scoped>
.chapter-content-item {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 18px;
  background: #fff;
}
.chapter-title {
  font-weight: bold;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}
.chapter-status-icon {
  width: 22px;
  height: 22px;
  margin-right: 8px;
}
.chapter-body {
  font-size: 15px;
  color: #333;
}
</style>
