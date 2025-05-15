/**
 * 模板事件处理模块
 * 处理模板相关的各种用户交互事件
 */
import { ElMessageBox } from 'element-plus'
import type { Template } from '../../../../types/template'
import type { TemplateState, TemplateApi } from '../types'

/**
 * 创建模板事件处理函数
 * @param state 模板状态对象
 * @param api 模板API交互对象
 */
export function createTemplateEvents(state: TemplateState, api: TemplateApi) {
  /**
   * 搜索处理
   */
  function handleSearch() {
    state.currentPage.value = 1
    api.loadTemplates()
  }

  /**
   * 处理页面大小变化
   */
  function handleSizeChange(size: number) {
    state.pageSize.value = size
    api.loadTemplates()
  }

  /**
   * 处理页面变化
   */
  function handleCurrentChange(page: number) {
    state.currentPage.value = page
    api.loadTemplates()
  }

  /**
   * 处理预览
   * 根据文件类型决定预览方式
   */
  async function handlePreview(template: Template) {
    if (!template || template.id === undefined || template.id === null) {
      console.error('无法预览：模板信息不完整或ID缺失', template)
      return { action: 'error', message: '无法预览：模板信息不完整或ID缺失' }
    }

    // 使用正确的属性名 fileType
    const type = (template.fileType || '').toLowerCase()
    
    // 如果是Markdown，通过路由导航
    if (type.includes('md')) {
      return { 
        action: 'navigate', 
        name: 'markdown-preview', 
        id: template.id 
      }
    }

    // 其他类型使用弹窗预览
    try {
      await api.getTemplatePreview(template.id)
      state.previewDocId.value = template.id
      state.previewVisible.value = true
      return { action: 'preview' }
    } catch (error) {
      return { 
        action: 'error', 
        message: '获取预览失败' 
      }
    }
  }

  /**
   * 处理添加模板
   */
  function handleAdd() {
    resetForm()
    state.editMode.value = false
    state.formVisible.value = true
  }

  /**
   * 处理编辑模板
   */
  function handleEdit(template: Template) {
    state.editMode.value = true
    state.uploadNewFile.value = false
    state.currentTemplate.value = template
    
    const { form } = state
    form.id = template.id
    form.title = template.title || ''
    form.content = template.content || ''
    form.outline_prompt = template.outline_prompt || ''
    form.subchapter_prompt = template.subchapter_prompt || ''
    form.content_prompt = template.content_prompt || ''
    form.file = null
    
    state.formVisible.value = true
  }

  /**
   * 处理删除模板
   */
  async function handleDelete(template: Template) {
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
      const success = await api.deleteTemplate(template.id)
      if (success) {
        api.loadTemplates()
      }
      return success
    } catch (error) {
      // 用户取消删除或删除失败
      return false
    }
  }

  /**
   * 处理文件选择
   */
  function handleFileChange(file: File) {
    state.form.file = file
  }

  /**
   * 重置表单
   */
  function resetForm() {
    const { form, formRef, fileUploaderRef } = state
    
    form.id = 0
    form.title = ''
    form.content = ''
    form.outline_prompt = ''
    form.subchapter_prompt = ''
    form.content_prompt = ''
    form.file = null
    
    if (formRef.value) {
      formRef.value.resetFields()
    }
    
    if (fileUploaderRef.value) {
      fileUploaderRef.value.clearFile()
    }
  }

  /**
   * 提交表单
   */
  async function submitForm() {
    const { formRef, submitting, formVisible } = state
    
    if (!formRef.value) return false
    
    try {
      const valid = await formRef.value.validate()
      if (!valid) return false
      
      submitting.value = true
      
      const success = await api.submitTemplateForm()
      if (success) {
        formVisible.value = false
        resetForm()
        api.loadTemplates()
      }
      
      return success
    } catch (error) {
      console.error('表单验证失败:', error)
      return false
    } finally {
      submitting.value = false
    }
  }

  return {
    handleSearch,
    handleSizeChange,
    handleCurrentChange,
    handlePreview,
    handleAdd,
    handleEdit,
    handleDelete,
    handleFileChange,
    resetForm,
    submitForm
  }
}
