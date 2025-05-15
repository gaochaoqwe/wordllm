<template>
  <el-dialog
    v-model="visible"
    title="编辑大纲生成提示词"
    width="600px"
    @close="onCancel"
  >
    <el-input
      v-model="prompt"
      type="textarea"
      :rows="8"
      placeholder="请输入大纲生成提示词"
    />
    <template #footer>
      <el-button @click="onCancel">
        取消
      </el-button>
      <el-button type="primary" @click="onConfirm">
        保存并重新生成
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineEmits, defineProps } from 'vue'

const props = defineProps<{
  modelValue: boolean
  initPrompt: string
}>()
const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = ref(props.modelValue)
const prompt = ref(props.initPrompt)

watch(() => props.modelValue, v => visible.value = v)
watch(() => props.initPrompt, v => prompt.value = v)

function onCancel() {
  emit('update:modelValue', false)
}
function onConfirm() {
  console.log(`[测试-Dialog] 确认按钮点击，当前提示词值: '${prompt.value}'`)
  emit('confirm', prompt.value)
  console.log('[测试-Dialog] 已发送confirm事件')
  emit('update:modelValue', false)
  console.log('[测试-Dialog] 已关闭对话框')
}

</script>

<!-- Ensure default export for SFC -->
<!-- This file uses <script setup>, which automatically provides a default export. No changes needed unless using classic API. -->
