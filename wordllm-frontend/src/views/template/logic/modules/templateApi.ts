/**
 * 模板API交互模块
 * 封装与模板相关的所有API调用
 */
import { ElMessage } from 'element-plus'
import { api } from '../../../../api/template'
import type { TemplateState } from '../types'

/**
 * 创建模板API交互函数
 * @param state 模板状态对象
 */
export function createTemplateApi(state: TemplateState) {
  /**
   * 加载模板列表
   */
  async function loadTemplates() {
    state.loading.value = true
    try {
      const response = await api.searchTemplates({
        title: state.searchTitle.value,
        page: state.currentPage.value - 1,
        size: state.pageSize.value
      })
      
      state.templates.value = response.content || []
      state.total.value = response.totalElements || 0
    } catch (error) {
      console.error('加载模板列表失败:', error)
      ElMessage.error('加载模板列表失败')
    } finally {
      state.loading.value = false
    }
  }

  /**
   * 获取模板预览
   */
  async function getTemplatePreview(templateId: number) {
    try {
      return await api.getTemplatePreview(templateId)
    } catch (error) {
      console.error('获取预览失败:', error)
      ElMessage.error('获取预览失败')
      throw error
    }
  }

  /**
   * 删除模板
   */
  async function deleteTemplate(templateId: number) {
    try {
      await api.deleteTemplate(templateId)
      ElMessage.success('删除成功')
      return true
    } catch (error) {
      console.error('删除模板失败:', error)
      ElMessage.error('删除模板失败')
      return false
    }
  }

  /**
   * 提交模板表单
   */
  async function submitTemplateForm() {
    const { form, editMode, uploadNewFile } = state
    
    try {
      if (editMode.value) {
        if (uploadNewFile.value && form.file) {
          // 编辑模式，上传新文件
          await api.uploadTemplate(
            form.file, 
            form.title, 
            form.content, 
            form.outline_prompt, 
            form.subchapter_prompt, 
            form.content_prompt
          )
        } else {
          // 编辑模式，只更新信息
          await api.updateTemplate(form.id, {
            title: form.title,
            content: form.content,
            outline_prompt: form.outline_prompt,
            subchapter_prompt: form.subchapter_prompt,
            content_prompt: form.content_prompt
          })
        }
        ElMessage.success('更新成功')
      } else {
        // 新建模式
        if (!form.file) {
          ElMessage.warning('请选择文件')
          return false
        }
        await api.uploadTemplate(
          form.file, 
          form.title, 
          form.content, 
          form.outline_prompt, 
          form.subchapter_prompt, 
          form.content_prompt
        )
        ElMessage.success('创建成功')
      }
      return true
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
      return false
    }
  }

  return {
    loadTemplates,
    getTemplatePreview,
    deleteTemplate,
    submitTemplateForm
  }
}
