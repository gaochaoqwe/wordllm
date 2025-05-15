<template>
  <el-dialog
    :model-value="modelValue"
    title="自定义要求"
    width="500px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="regenerate-form">
      <p class="hint-text">
        输入自定义要求可以让AI按照您的需求重新生成章节目录
      </p>
      <el-input
        v-model="requirement"
        type="textarea"
        rows="4"
        placeholder="请输入自定义要求..."
      />
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="cancel">取消</el-button>
        <el-button type="primary" @click="confirm">确认重新生成</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script lang="ts">
import { ref, watch, defineComponent } from 'vue'

export default defineComponent({
  name: 'RegenerateRequirementDialog',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    defaultRequirement: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'confirm', 'cancel'],
  setup(props, { emit }) {
    const requirement = ref(props.defaultRequirement)
    
    // 监听props.defaultRequirement的变化
    watch(() => props.defaultRequirement, (newVal) => {
      requirement.value = newVal
    })
    
    // 监听modelValue，当对话框打开时重置需求文本
    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        requirement.value = props.defaultRequirement
      }
    })
    
    // 取消
    function cancel() {
      emit('update:modelValue', false)
      emit('cancel')
    }
    
    // 确认
    function confirm() {
      emit('update:modelValue', false)
      emit('confirm', requirement.value)
    }
    
    return {
      requirement,
      cancel,
      confirm
    }
  }
})
</script>

<style scoped>
.regenerate-form {
  padding: 10px 0;
}
.hint-text {
  color: #606266;
  margin-bottom: 10px;
  font-size: 14px;
}
</style>
