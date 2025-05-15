import { onMounted } from 'vue'
import { useChapterState } from './useChapterState'
import { useChapterOperations } from './useChapterOperations'
import { useContentGeneration } from './useContentGeneration'

// 直接定义类型，避免导入问题
export interface Chapter {
  chapterNumber: string;
  title: string;
  content?: string;
  dbId?: string | number;
  project_id?: string | number;
}

let singleton: ReturnType<typeof createDocumentEditor> | null = null;

function createDocumentEditor() {
  // 获取章节状态
  const chapterState = useChapterState()
  
  // 获取章节操作功能
  const operations = useChapterOperations(
    chapterState.currentChapter,
    chapterState.chapterContent,
    chapterState.documentContents
  )
  
  // 获取内容生成功能
  const generation = useContentGeneration(
    chapterState.chapters,
    chapterState.currentChapter,
    chapterState.chapterContent,
    chapterState.documentContents,
    chapterState.chapterStatuses,
    chapterState.isGenerating,
    chapterState.autoGenerating,
    chapterState.currentGeneratingIndex,
    chapterState.generationProgress,
    operations.saveChapterContent,
    chapterState.handleSelectChapter
  )
  
  // 初始化数据
  onMounted(chapterState.initializeData)
  
  // 返回所有功能
  return {
    // 从 chapterState 导出
    ...chapterState,
    
    // 从 operations 导出
    ...operations,
    
    // 从 generation 导出
    ...generation
  }
}

export function useDocumentEditor() {
  if (!singleton) singleton = createDocumentEditor();
  return singleton;
}

