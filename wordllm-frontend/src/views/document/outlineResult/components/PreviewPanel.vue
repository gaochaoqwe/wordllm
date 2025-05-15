<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="'80%'"
    :top="'5vh'"
    :fullscreen="true"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="preview-container">
      <component
        :is="DocxPreviewComponent"
        v-if="filePath"
        :file-path="filePath"
        style="height: 100%"
      />
      <div v-else class="empty-preview">
        暂无预览内容
      </div>
    </div>
  </el-dialog>
</template>

<script lang="ts">
import { defineComponent, defineAsyncComponent, ref } from 'vue'

// 导入DocxPreview组件
// 使用defineAsyncComponent异步加载组件
const DocxPreviewComponent = defineAsyncComponent(() => import('../../../../components/DocxPreview.vue'))

export default defineComponent({
  name: 'PreviewPanel',
  components: {
    DocxPreviewComponent
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: '文档预览'
    },
    filePath: {
      type: String,
      default: null
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const updateModelValue = (value: boolean) => {
      emit('update:modelValue', value)
    }
    
    return {
      updateModelValue
    }
  }
})
</script>

<style scoped>
.preview-container {
  height: 80vh;
  overflow: hidden;
}
.empty-preview {
  color: #bbb;
  text-align: center;
  padding: 80px 0;
}
</style>
