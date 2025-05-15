import { ElMessage } from 'element-plus'

// 临时定义Chapter接口以避免循环依赖
interface Chapter {
  chapterNumber: string;
  title: string;
  content?: string;
  dbId?: string | number;
  project_id?: string | number;
}

export function useChapterOperations(currentChapter, chapterContent, documentContents) {
  // 保存章节内容到数据库
  const saveChapterContent = async (chapter: Chapter, content: string) => {
    if (!chapter) {
      ElMessage.error('No chapter selected')
      return false
    }
    
    try {
      // 先在本地存储内容
      documentContents.value[chapter.chapterNumber] = content
      
      // 发送到服务器
      const response = await fetch(`/api/chapters/${chapter.dbId}/content`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: content
        })
      })
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to save content')
      }
      
      ElMessage.success('Chapter content saved successfully')
      return true
    } catch (error) {
      console.error('Error saving chapter content:', error)
      ElMessage.error('Failed to save content: ' + (error instanceof Error ? error.message : 'Unknown error'))
      return false
    }
  }

  // 保存当前章节内容
  const saveContent = async () => {
    if (!currentChapter.value) {
      ElMessage.warning('Please select a chapter first')
      return
    }
    
    await saveChapterContent(currentChapter.value, chapterContent.value)
  }
  
  return {
    saveChapterContent,
    saveContent
  }
}
