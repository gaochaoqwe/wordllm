import { ElMessage } from 'element-plus'
import { outlineState } from './outlineState'
import { Chapter } from './types'

// 获取模板详情
export async function fetchTemplateDetails(templateId: number) {
  try {
    const res = await fetch(`/api/templates/${templateId}`)
    const data = await res.json()
    if (data.success && data.data) {
      return data.data
    }
    return null
  } catch (error) {
    console.error('获取模板详情失败:', error)
    return null
  }
}

// 获取章节数据
export async function fetchChapters(projectId: string | number) {
  if (!projectId) {
    console.error('[ERROR] 获取章节出错: projectId不能为空')
    throw new Error('项目ID不能为空')
  }

  console.log('[DEBUG-1] 开始获取章节目录，projectId:', projectId, '类型:', typeof projectId)
  
  // 确保 projectId 是数字类型，后端需要整数型
  const numericProjectId = Number(projectId)
  if (isNaN(numericProjectId)) {
    console.error('[ERROR] projectId不是有效数字:', projectId)
    throw new Error('无效的项目ID')
  }
  
  const apiUrl = `/api/projects/${numericProjectId}/chapters`
  console.log('[DEBUG-1.5] 发送请求到:', apiUrl)
  
  // Normalize keys to camelCase for frontend
  function normalizeChapter(chapter: any) {
    if (!chapter) return {};
    return {
      ...chapter,
      chapterNumber: chapter.chapterNumber || chapter.chapter_number || '',
      title: chapter.title || '',
      children: Array.isArray(chapter.children) ? chapter.children.map(normalizeChapter) : []
    };
  }
  
  try {
    const res = await fetch(apiUrl)
    console.log('[DEBUG-2] fetch请求已完成，开始转换JSON')
    const data = await res.json()
    console.log('[DEBUG-3] 原始数据类型:', typeof data)
    console.log('[DEBUG-4] 原始数据内容:', data)
    
    // 处理不同的响应结构
    let chapterArr: Chapter[] = []
    if (data.data && typeof data.data === 'object') {
      console.log('[DEBUG-8] data.data.chapters 存在性:', !!data.data.chapters)
      if (Array.isArray(data.data.chapters)) {
        console.log('[DEBUG-9] data.data.chapters 是数组，长度:', data.data.chapters.length)
        chapterArr = data.data.chapters.map(normalizeChapter)
      } else if (data.data.chapter_list && Array.isArray(data.data.chapter_list)) {
        console.log('[DEBUG-10] data.data.chapter_list 是数组，长度:', data.data.chapter_list.length)
        chapterArr = data.data.chapter_list.map(normalizeChapter)
      } else if (Array.isArray(data.data)) {
        console.log('[DEBUG-11] data.data 自身是数组，长度:', data.data.length)
        chapterArr = data.data.map(normalizeChapter)
      }
    } else if (Array.isArray(data)) {
      console.log('[DEBUG-12] data 自身是数组，长度:', data.length)
      chapterArr = data.map(normalizeChapter)
    }
    
    console.log('[DEBUG-13] 最终确定的 chapterArr:', chapterArr)
    console.log('[DEBUG-14] 最终确定的 chapterArr 长度:', chapterArr.length)
    // Debug log for assignment
    setTimeout(() => {
      console.log('[DEBUG-FRONTEND] chapters.value 即将被设置:', chapterArr)
    }, 0);
    return chapterArr
  } catch (error) {
    console.error('获取章节数据失败:', error)
    throw error
  }
}

// 保存章节到数据库
export async function saveChaptersToDB() {
  const projectId = outlineState.projectId.value
  if (!projectId) {
    throw new Error('未找到项目ID，无法保存章节')
  }
  
  if (!outlineState.chapters.value || outlineState.chapters.value.length === 0) {
    throw new Error('没有章节数据可保存')
  }
  
  try {
    const response = await fetch(`/api/projects/${projectId}/chapters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chapters: outlineState.chapters.value
      })
    })
    
    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '保存章节失败')
    }
    
    ElMessage.success('章节目录已保存到数据库')
    return data
  } catch (error) {
    console.error('批量保存章节目录失败:', error)
    ElMessage.error('批量保存章节目录失败: ' + (error instanceof Error ? error.message : '未知错误'))
    throw error
  }
}

// 继续生成子章节
export async function continueGenerateSubchapters(useRequirement = false, requirement = '') {
  const projectId = outlineState.projectId.value
  const templateId = outlineState.templateId.value
  
  if (!projectId || !templateId) {
    throw new Error('项目ID或模板ID不存在，无法继续生成')
  }
  
  if (!outlineState.chapters.value || outlineState.chapters.value.length === 0) {
    throw new Error('没有章节数据，无法继续生成')
  }
  
  try {
    // 准备请求参数
    const requestBody = {
      project_id: projectId,
      template_id: templateId,
      chapters: outlineState.chapters.value
    }
    
    if (useRequirement && requirement) {
      requestBody['requirement'] = requirement
    }
    
    // 调用API继续生成子章节
    const response = await fetch('/api/outlines/generate-subchapters', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    const result = await response.json()
    if (!result.success) {
      throw new Error(result.message || '生成子章节失败')
    }
    
    // 更新章节数据
    if (result.data && Array.isArray(result.data.chapters)) {
      outlineState.chapters.value = result.data.chapters
      outlineState.hasGeneratedSubchapters.value = true
      
      // 保存到数据库
      await saveChaptersToDB()
      
      return result.data
    } else {
      throw new Error('返回数据格式不正确')
    }
  } catch (error) {
    console.error('生成子章节失败:', error)
    throw error
  }
}

// 生成文档内容
export async function generateDocumentContent() {
  const projectId = outlineState.projectId.value
  const templateId = outlineState.templateId.value
  
  if (!projectId || !templateId) {
    throw new Error('项目ID或模板ID不存在，无法生成文档内容')
  }
  
  if (!outlineState.chapters.value || outlineState.chapters.value.length === 0) {
    throw new Error('无可用的章节数据')
  }
  
  try {
    // 1. 先确保章节保存到数据库
    await saveChaptersToDB()
    
    // 2. 调用后端接口启动异步生成任务
    const postBody = {
      template_id: templateId,
      project_id: projectId,
      chapters: outlineState.chapters.value.map(ch => ({
        chapterNumber: ch.chapterNumber,
        title: ch.title
      }))
    }
    
    console.log('[前端调试] generateDocument POST /api/documents/start-generate-content 请求体:', postBody)
    
    const res = await fetch('/api/documents/start-generate-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(postBody)
    })
    
    const result = await res.json()
    console.log('result:', result)
    
    if (result.success) {
      return {
        success: true,
        projectId: projectId
      }
    } else {
      throw new Error(result.message || '启动文档内容生成失败')
    }
  } catch (error) {
    console.error('生成文档内容错误:', error)
    throw error
  }
}
