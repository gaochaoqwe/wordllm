<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Template } from '../../types/template'
import { api } from '../../api/template'

const route = useRoute()
const router = useRouter()
const templateId = route.params.id ? Number(route.params.id) : undefined
const formRef = ref<FormInstance>()

// 扩展Template类型，添加modelId属性
interface TemplateForm extends Partial<Template> {
  modelId?: string;
}

const template = ref<TemplateForm>({
  title: '',
  content: '',
  modelId: ''
})

const loading = ref(false)

onMounted(async () => {
  try {
    loading.value = true
    // 如果是编辑模式，加载模板数据
    if (templateId) {
      const data = await api.getTemplate(templateId)
      if (data) {
        template.value = {
          ...template.value,
          ...data
        }
      }
    }
  } catch (error) {
    console.error('Failed to load models or template:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})

// 表单验证函数
const validateFormData = () => {
  if (!template.value.title?.trim()) {
    ElMessage.warning('请输入模板标题')
    return false
  }
  if (!template.value.content?.trim()) {
    ElMessage.warning('请输入模板内容')
    return false
  }
  if (!template.value.modelId) {
    ElMessage.warning('请选择模型')
    return false
  }
  return true
}

const handleSubmit = async function handleSubmit() {
  if (!formRef.value) return

  try {
    // 验证表单
    if (!validateFormData()) return
    await formRef.value.validate()

    // 准备提交数据
    const submitData = {
      title: template.value.title?.trim(),
      content: template.value.content?.trim(),
      status: template.value.status || 'PENDING'
    }

    loading.value = true

    // 根据是否有ID决定是更新还是创建
    if (templateId) {
      await api.updateTemplate(templateId, submitData)
      ElMessage.success('模板更新成功')
    } else {
      // 创建新模板
      await api.createTemplate(submitData)
      ElMessage.success('模板创建成功')
    }
    
    router.push('/templates')
  } catch (error) {
    console.error('Failed to submit:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="template-edit">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ templateId ? '编辑模板' : '创建模板' }}</span>
        </div>
      </template>

      <el-form 
        ref="formRef"
        :model="template" 
        label-width="120px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="模板名称" required>
          <el-input v-model="template.title" placeholder="请输入模板名称" />
        </el-form-item>

        <el-form-item label="模板描述">
          <el-input 
            v-model="template.content" 
            type="textarea" 
            :rows="3"
            placeholder="请输入模板描述"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="template.status">
            <el-option label="待处理" value="PENDING" />
            <el-option label="处理中" value="PROCESSING" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="错误" value="ERROR" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择模型" required>
          <el-select v-model="template.modelId" placeholder="请选择模型">
            <!-- 作为示例添加一个默认选项，真实模型数据应从服务器加载 -->
            <el-option
              label="默认模型"
              value="1"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleSubmit"
          >
            保存
          </el-button>
          <el-button 
            @click="router.push('/templates')"
          >
            取消
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.template-edit {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
