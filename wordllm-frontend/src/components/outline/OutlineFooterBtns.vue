<template>
  <div class="footer-btns">
    <template v-if="!hasGeneratedSubchapters">
      <el-button plain @click="$emit('regenerate')" style="margin-right: 16px;">章节不满意？重新生成</el-button>
      <el-button type="primary" @click="$emit('continue-generate')">继续生成多级目录大纲</el-button>
    </template>
    <template v-else>
      <el-button plain @click="$emit('regenerate-subchapters')" style="margin-right: 16px;">子章节不满意？重新生成</el-button>
      <el-button 
        type="success" 
        @click="$emit('generate-document')" 
        :loading="isGeneratingDocument"
      >
        {{ isGeneratingDocument ? '编写中...' : '一键撰写文档内容' }}
      </el-button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
const props = defineProps({
  hasGeneratedSubchapters: Boolean,
  isGeneratingDocument: Boolean
})
</script>

<style scoped>
.footer-btns {
  display: flex;
  justify-content: center;
  margin-top: auto;
  padding-top: 16px;
}
</style>
