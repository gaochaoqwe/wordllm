<template>
  <!-- 使用单一根元素包裹所有内容 -->
  <div class="template-list-container">
    <div class="header">
      <h2>模板管理</h2>
      <div class="actions">
        <el-input
          v-model="searchTitle"
          placeholder="搜索模板标题"
          clearable
          style="width: 200px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新建模板
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="list-card">
      <el-table
        v-loading="loading"
        :data="templates"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.content || '暂无描述' }}
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="100" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              size="small"
              @click="previewTemplate(row)"
            >
              预览
            </el-button>
            <el-button 
              link 
              type="primary" 
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button 
              link 
              type="danger" 
              size="small"
              @click="deleteTemplate(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          @update:current-page="(val) => currentPage = val"
          @update:page-size="(val) => pageSize = val"
        />
      </div>
    </el-card>

    <!-- 模板表单对话框 -->
    <el-dialog
      v-model="formVisible"
      :title="editMode ? '编辑模板' : '新建模板'"
      width="500px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入模板标题" />
        </el-form-item>
        <el-form-item label="描述" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        
        <el-form-item label="大纲提示词" prop="outline_prompt">
          <el-input
            v-model="form.outline_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入大纲生成自定义提示词"
          />
        </el-form-item>
        
        <el-form-item label="子章节提示词" prop="subchapter_prompt">
          <el-input
            v-model="form.subchapter_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入子章节生成自定义提示词"
          />
        </el-form-item>
        
        <el-form-item label="内容提示词" prop="content_prompt">
          <el-input
            v-model="form.content_prompt"
            type="textarea"
            :rows="2"
            placeholder="请输入内容生成自定义提示词"
          />
        </el-form-item>
        <el-form-item v-if="!editMode || uploadNewFile" label="文件" prop="file">
          <file-uploader
            ref="fileUploaderRef"
            :accept="'.docx,.doc,.pdf,.txt'"
            @file-selected="handleFileChange"
          />
        </el-form-item>
        <el-form-item v-if="editMode">
          <el-checkbox v-model="uploadNewFile">
            更新文件
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 文档预览组件 -->
    <DocxPreview
      v-model="previewVisible"
      :document-id="previewDocId"
      dialog-mode
      :dialog-title="'文档预览'"
      style="z-index: 3000;"
    />
  </div>
</template>

<script setup lang="ts">
// 导入组件
import * as DocxPreviewModule from '../../components/DocxPreview.vue'
const DocxPreview = DocxPreviewModule

// 导入类型定义
import type { Template } from '../../types/template'

// 导入 Element Plus 组件和依赖
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import FileUploader from '../../components/FileUploader.vue'
import { useRouter } from 'vue-router'
import { api } from '../../api/template'

// 导入模板管理逻辑
import { useTemplateManager } from './logic/templateManager'

// 路由
const router = useRouter()

// 使用模板管理逻辑
const {
  // 状态
  loading,
  templates,
  total,
  currentPage,
  pageSize,
  searchTitle,
  formVisible,
  submitting,
  editMode,
  uploadNewFile,
  currentTemplate,
  previewVisible,
  previewDocId,
  formRef,
  fileUploaderRef,
  form,
  rules,
  
  // 方法
  loadTemplates,
  handleSearch,
  handleSizeChange,
  handleCurrentChange,
  formatDate,
  formatFileSize,
  handleFileChange,
  resetForm,
  submitForm
} = useTemplateManager()

// 预览处理
async function previewTemplate(template: Template) {
  if (!template || template.id === undefined || template.id === null) {
    console.error('无法预览：模板信息不完整或ID缺失', template)
    ElMessage.error('无法预览：模板信息不完整或ID缺失')
    return
  }

  const type = (template.fileType || '').toLowerCase()
  if (type.includes('md')) {
    router.push({ name: 'markdown-preview', params: { id: template.id } })
    return
  }

  try {
    await api.getTemplatePreview(template.id)
    previewDocId.value = template.id
    previewVisible.value = true
  } catch (error) {
    console.error('获取预览失败:', error)
    ElMessage.error('获取预览失败')
  }
}

// 添加处理
function handleAdd() {
  resetForm()
  editMode.value = false
  formVisible.value = true
}

// 编辑处理
function handleEdit(template: Template) {
  editMode.value = true
  uploadNewFile.value = false
  currentTemplate.value = template
  
  form.id = template.id
  form.title = template.title
  form.content = template.content || ''
  // 使用正确的属性名（与form的字段名称匹配）
  form.outline_prompt = template.outline_prompt || ''
  form.subchapter_prompt = template.subchapter_prompt || ''
  form.content_prompt = template.content_prompt || ''
  form.file = null
  
  formVisible.value = true
}

// 删除处理
async function deleteTemplate(template: Template) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.title}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 用户确认删除
    await api.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    // 用户取消删除或删除失败
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除模板失败')
    }
  }
}

// 页面加载后自动获取模板列表
loadTemplates()
</script>

<style scoped>
.template-list-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.list-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-list) {
  width: 100%;
}
</style>
