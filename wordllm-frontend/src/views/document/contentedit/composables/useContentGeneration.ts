import { ElMessage } from 'element-plus'
import { ref } from 'vue'

export function useContentGeneration(
  chapters, 
  currentChapter, 
  chapterContent, 
  documentContents, 
  chapterStatuses, 
  isGenerating,
  autoGenerating,
  currentGeneratingIndex,
  generationProgress,
  saveChapterContent,
  handleSelectChapter
) {
  // 存储当前项目信息
  const projectInfo = ref(null);

  // 从后端获取项目详情（包含模板ID）
  const fetchProjectInfo = async (projectId) => {
    try {
      console.log('[前端调试] 开始获取项目详情, projectId:', projectId);
      const response = await fetch(`/api/projects/${projectId}`);
      console.log('[前端调试] 项目详情响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`获取项目详情失败: ${response.status}`);
      }
      
      const responseText = await response.text();
      console.log('[前端调试] 项目详情原始响应内容:', responseText);
      
      let result;
      try {
        result = JSON.parse(responseText);
      } catch (e) {
        console.error('[前端调试] 项目详情响应不是有效JSON:', e);
        throw new Error('项目详情响应不是有效JSON');
      }
      
      console.log('[前端调试] 项目详情解析后结果:', result);
      console.log('[前端调试] 项目详情是否有success字段:', !!result.success);
      console.log('[前端调试] 项目详情是否有data字段:', !!result.data);
      
      if (result.success && result.data) {
        projectInfo.value = result.data;
        console.log('[前端调试] 获取到项目详情:', projectInfo.value);
        console.log('[前端调试] 项目详情是否包含template_id:', Object.prototype.hasOwnProperty.call(result.data, 'template_id'));
        console.log('[前端调试] 项目模板ID值:', result.data.template_id);
        return result.data;
      } else {
        console.error('[前端调试] 项目详情接口成功但未返回有效数据:', result);
      }
    } catch (error) {
      console.error('[前端调试] 获取项目详情出错:', error);
      ElMessage.error(`获取项目详情失败: ${error.message}`);
    }
    return null;
  };

  // 生成当前选中章节的内容
  const generateContent = async () => {
    if (!currentChapter.value) {
      ElMessage.warning('Please select a chapter first')
      return null
    }
    
    isGenerating.value = true
    
    // 更新状态为生成中
    if (currentChapter.value) {
      chapterStatuses.value[currentChapter.value.chapterNumber] = 'generating'
    }
    
    console.log('Preparing to get project ID')
    // 从多个来源尝试获取 project_id
    let projectId = null
    
    // 来源1: 从章节数组第一项
    if (chapters.value && chapters.value.length > 0) {
      projectId = chapters.value[0].project_id
      console.log('Getting project_id from chapter array:', projectId)
    }
    
    // 来源2: URL 查询参数
    if (!projectId) {
      const urlParams = new URLSearchParams(window.location.search)
      // 同时支持 projectId（前端页面的命名风格）和 project_id（API 的命名风格）
      projectId = urlParams.get('projectId') || urlParams.get('project_id')
      console.log('Getting project_id from URL parameter:', projectId)
    }
    
    // 来源3: localStorage
    if (!projectId) {
      projectId = localStorage.getItem('currentProjectId')
      console.log('Getting project_id from localStorage:', projectId)
    }
    
    // 来源4: URL 路径
    if (!projectId) {
      const projectMatch = window.location.pathname.match(/\/projects\/(\d+)/)
      if (projectMatch && projectMatch[1]) {
        projectId = projectMatch[1]
        console.log('Getting project_id from URL path:', projectId)
      }
    }
    
    // 如果仍未找到，使用默认值
    if (!projectId) {
      projectId = 18 // 使用后端日志中的默认项目ID
      console.log('Using default project ID:', projectId)
    }
    
    // 存储项目ID供下次使用
    if (projectId) {
      localStorage.setItem('currentProjectId', projectId.toString())
    }
    
    try {
      console.log('Preparing to send fetch request, project ID:', projectId)
      
      // 先获取项目详情，读取 template_id
      if (!projectInfo.value) {
        await fetchProjectInfo(projectId);
      }
      
      const template_id = projectInfo.value?.template_id;
      console.log('[前端调试] 使用项目详情获取到模板ID:', template_id);
      
      if (!template_id) {
        console.error('[前端调试] 项目没有绑定模板ID，尝试使用 localStorage 备用值');
      }
      
      const reqBody = {
        template_id: template_id || localStorage.getItem('templateId'),
        project_id: projectId,
        chapter_number: currentChapter.value.chapterNumber,
        chapters: [currentChapter.value]
      };
      console.log('[前端调试] 发送 /api/documents/generate-content 请求体:', reqBody);
      
      if (!reqBody.template_id) {
        throw new Error('模板ID缺失，无法生成文档内容。请先选择模板。');
      }
      
      const response = await fetch('/api/documents/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reqBody)
      });
      console.log('[前端调试] fetch 响应状态:', response.status);
      if (!response.ok) {
        const errText = await response.text();
        console.error('[前端调试] fetch 失败，响应内容:', errText);
        throw new Error('API error: ' + response.status + ' ' + errText);
      }
      
      const data = await response.json()
      console.log('Received response data:', data)
      
      let generatedContent = ''
      let realContent = null

      if (data && data.data && typeof data.data.content === 'string') {
        // 处理后端返回的JSON字符串中的\n，将其转换为实际的换行符
        realContent = data.data.content.replace(/\\n/g, '\n')
        console.log('[前端调试] 处理换行符后的内容片段:', realContent.substring(0, 100))
      } else if (data && data.data && data.data.content !== null && typeof data.data.content !== 'undefined') {
        console.warn('API returned non-string content, using placeholder:', data.data.content)
      }

      if (realContent !== null) {
        console.log('Using API returned content')
        generatedContent = realContent
      } else {
        console.log('API did not return content or content was not a string, using example content')
        const title = currentChapter.value && currentChapter.value.title ? currentChapter.value.title : 'default_title'
        generatedContent = 'This is auto-generated example content for "' + title + '".'
      }
      
      // 更新UI
      chapterContent.value = generatedContent
      console.log('Content updated to editor')
      
      // 保存生成的内容到内存
      if (currentChapter.value) {
        // 保存到前端内存
        documentContents.value[currentChapter.value.chapterNumber] = generatedContent
        // 设置状态为完成
        chapterStatuses.value[currentChapter.value.chapterNumber] = 'done'
        
        // 注意: 不需要再次保存到数据库，后端已经在生成内容时完成了保存
        // await saveChapterContent(currentChapter.value, generatedContent)
      }
      
      isGenerating.value = false
      return generatedContent
    } catch (error) {
      // 错误处理
      console.error('Failed to generate chapter content:', error)
      ElMessage.error('Content generation failed: ' + (error instanceof Error ? error.message : 'Unknown error'))
      
      // 更新状态为失败
      if (currentChapter.value) {
        chapterStatuses.value[currentChapter.value.chapterNumber] = 'failed'
      }
      
      isGenerating.value = false
      return null
    }
  }

  // 处理来自AI聊天框的内容生成请求
  const handleGenerateContent = (content: string) => {
    if (!currentChapter.value) {
      ElMessage.warning('Please select a chapter first')
      return
    }
    
    chapterContent.value = content
    // 自动保存AI生成的内容
    if (currentChapter.value) {
      saveChapterContent(currentChapter.value, content)
    }
  }

  // 自动生成所有章节内容
  const autoGenerateAllContent = async () => {
    if (autoGenerating.value) {
      ElMessage.warning('Already generating all content, please wait')
      return
    }
    
    if (!chapters.value || chapters.value.length === 0) {
      ElMessage.warning('No chapters found')
      return
    }
    
    autoGenerating.value = true
    currentGeneratingIndex.value = 0
    generationProgress.value = 0
    
    const totalChapters = chapters.value.length
    
    for (let i = 0; i < totalChapters; i++) {
      currentGeneratingIndex.value = i
      generationProgress.value = Math.floor((i / totalChapters) * 100)
      
      const chapter = chapters.value[i]
      if (!chapter) continue
      
      // 跳过已有内容的章节
      if (documentContents.value[chapter.chapterNumber] && 
          documentContents.value[chapter.chapterNumber].trim() !== '') {
        console.log(`Chapter ${chapter.chapterNumber} already has content, skipping...`)
        continue
      }
      
      // 选择章节
      handleSelectChapter(chapter)
      
      // 生成内容
      console.log(`Generating content for chapter ${i+1}/${totalChapters}: ${chapter.title}`)
      
      try {
        await generateContent()
        // 添加小延迟以防止API速率限制
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        console.error(`Error generating content for chapter ${chapter.chapterNumber}:`, error)
        // 即使此章节失败，也继续下一章节
      }
    }
    
    generationProgress.value = 100
    autoGenerating.value = false
    ElMessage.success(`Completed content generation for ${totalChapters} chapters`)
  }

  return {
    generateContent,
    fetchProjectInfo,
    projectInfo,
    handleGenerateContent,
    autoGenerateAllContent
  }
}
