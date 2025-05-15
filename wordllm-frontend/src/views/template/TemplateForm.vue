<template>
  <div class="template-form">
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模板' : '新建模板'"
      width="50%"
      :close-on-click-modal="false"
      :before-close="handleClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入模板标题" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        
        <el-form-item label="文件" prop="file">
          <file-uploader 
            ref="fileUploaderRef"
            :accept="'.docx,.doc,.pdf,.txt'"
            @file-selected="handleFileSelected"
          />
        </el-form-item>

        <el-form-item label="大纲生成提示词" prop="outline_prompt">
          <el-input
            v-model="form.outline_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入大纲生成自定义提示词"
          />
        </el-form-item>
        <el-form-item label="子章节生成提示词" prop="subchapter_prompt">
          <el-input
            v-model="form.subchapter_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入子章节生成自定义提示词"
          />
        </el-form-item>
        <el-form-item label="内容生成提示词" prop="content_prompt">
          <el-input
            v-model="form.content_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入内容生成自定义提示词"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
// 引入 FileUploader 组件
import FileUploader from '../../components/FileUploader.vue'
// 定义组件类型
interface IFileUploader {
  clearFile: () => void;
  setFile: (file: File, fileUrl?: string) => void;
  getFile: () => File | null;
  getFileUrl: () => string | null;
}
import type { Template } from '../../types/template'
import api from '../../api/template'
import { computed } from 'vue'

// 组件接收的参数
const props = defineProps<{
  modelValue: boolean
  editTemplate?: Template | null
}>()

// 组件发出的事件
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit'): void
  (e: 'cancel'): void
}>()

// 组件内部状态
const dialogVisible = ref(props.modelValue)
const submitting = ref(false)
const formRef = ref<FormInstance>()
// 使用定义的接口类型为组件ref声明类型
const fileUploaderRef = ref<IFileUploader | null>(null)

// 表单数据
const form = reactive({
  id: 0,
  title: '',
  description: '',
  file: null as File | null,
  outline_prompt: '',
  subchapter_prompt: '',
  content_prompt: ''
})

// 表单校验规则
const rules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度应在2-50个字符之间', trigger: 'blur' }
  ]
})

// 是否为编辑模式
const isEdit = computed(() => !!props.editTemplate?.id)

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.editTemplate) {
    // 编辑模式，填充表单
    form.id = props.editTemplate.id
    form.title = props.editTemplate.title
    form.description = props.editTemplate.content || ''
    form.file = null
  } else if (newVal) {
    // 新建模式，重置表单
    resetForm()
  }
})

// 监听dialog内部状态变化
watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 重置表单
function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  form.id = 0
  form.title = ''
  form.description = ''
  form.file = null
  
  // 重置文件上传组件
  if (fileUploaderRef.value) {
    fileUploaderRef.value.clearFile()
  }
}

// 处理文件选择
function handleFileSelected(file: File) {
  form.file = file
}

// 处理表单提交
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      submitting.value = true
      
      if (isEdit.value) {
        // 编辑模式
        if (form.file) {
          // 有新文件，更新文件和信息
          await api.uploadTemplate(form.file, form.title, form.description)
        } else {
          // 只更新信息
          await api.updateTemplate(form.id, {
            title: form.title,
            content: form.description,
            outline_prompt: form.outline_prompt,
            subchapter_prompt: form.subchapter_prompt,
            content_prompt: form.content_prompt
          })
        }
        ElMessage.success('模板更新成功')
      } else {
        // 新建模式
        if (!form.file) {
          ElMessage.warning('请选择一个文件')
          return
        }
        await api.uploadTemplate(
          form.file,
          form.title,
          form.description,
          form.outline_prompt,
          form.subchapter_prompt,
          form.content_prompt
        )
        ElMessage.success('模板创建成功')
      }
      
      // 关闭对话框并通知父组件
      dialogVisible.value = false
      emit('submit')
    } catch (error) {
      console.error('提交模板失败:', error)
      ElMessage.error('操作失败: ' + (error instanceof Error ? error.message : '未知错误'))
    } finally {
      submitting.value = false
    }
  })
}

// 处理关闭对话框
function handleClose() {
  resetForm()
  dialogVisible.value = false
  emit('cancel')
}
</script>

<style scoped>
.template-form {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
