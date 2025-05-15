<template>
  <el-tree
    :data="treeChapters"
    :props="{ label: 'title', children: 'children' }"
    node-key="chapterNumber"
    default-expand-all
    style="width: 100%; margin-bottom: 16px;"
  >
    <template #default="{ node, data }">
      <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
        <span>{{ data.chapterNumber }} {{ data.title }}</span>
        <span>
          <el-button link type="primary" size="small" @click.stop="emitAddRequirement(data)">添加要求</el-button>
          <el-button link type="danger" size="small" @click.stop="emitRemoveChapter(data)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </span>
      </div>
    </template>
  </el-tree>
</template>

<script setup lang="ts">
import { computed, defineProps, defineEmits } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
  chapters: {
    type: Array,
    required: true
  }
})
const emits = defineEmits(['add-requirement', 'remove-chapter'])

function flatToTree(flatChapters: any[]) {
  const map: Record<string, any> = {}
  const roots: any[] = []
  flatChapters.forEach(ch => {
    map[ch.chapterNumber] = { ...ch, children: [] }
  })
  flatChapters.forEach(ch => {
    const parentNum = ch.chapterNumber.split('.').slice(0, -1).join('.')
    if (parentNum && map[parentNum]) {
      map[parentNum].children.push(map[ch.chapterNumber])
    } else {
      roots.push(map[ch.chapterNumber])
    }
  })
  return roots
}
const treeChapters = computed(() => flatToTree(props.chapters))

function emitAddRequirement(data: any) {
  emits('add-requirement', data)
}
function emitRemoveChapter(data: any) {
  emits('remove-chapter', data)
}
</script>

<style scoped>
</style>
