import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

// 临时定义Chapter接口以避免循环依赖
interface Chapter {
  chapterNumber: string;
  title: string;
  content?: string;
  dbId?: string | number;
  project_id?: string | number;
}

export function useChapterState() {
  // 基础状态
  const chapters = ref<Chapter[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const chapterContent = ref('')
  const documentContents = ref<Record<string, string>>({})
  const chapterStatuses = ref<Record<string, string>>({})
  
  // 处理状态
  const isGenerating = ref(false)
  const autoGenerating = ref(false)
  const currentGeneratingIndex = ref(0)
  const generationProgress = ref(0)
  
  // 路由
  const route = useRoute()
  
  // 选择章节
  const handleSelectChapter = (chapter: Chapter) => {
    console.log('[useChapterState] handleSelectChapter 被调用，参数：', chapter)
    currentChapter.value = chapter
    console.log('[useChapterState] currentChapter 已赋值：', currentChapter.value)
    if (chapter) {
      chapterContent.value = documentContents.value[chapter.chapterNumber] || ''
    }
  }
  
  // 监听章节变化，更新编辑器内容
  watch(currentChapter, (newChapter) => {
    if (newChapter) {
      chapterContent.value = documentContents.value[newChapter.chapterNumber] || ''
    } else {
      chapterContent.value = ''
    }
  })
  
  // 初始化数据
  const initializeData = async () => {
    console.log('Page loaded - DocumentEditor')
    console.log('----------------- Debug Info Start -----------------')

    // 从路由参数获取 projectId
    const projectId = route.query.projectId
    if (!projectId) {
      ElMessage.error('Project ID not found, please generate outline and save directory first')
      return
    }

    // 1. 拉取章节目录
    let chapterList = []
    try {
      const res = await fetch(`/api/projects/${projectId}/chapters`)
      const data = await res.json()
      if (!data.success) throw new Error(data.message || 'Failed to get chapter outline')
      chapterList = data.data || []
      console.log('Chapters fetched from database:', chapterList)
    } catch (err) {
      ElMessage.error('Failed to get chapter outline: ' + (err instanceof Error ? err.message : 'Unknown error'))
      return
    }

    // 2. 拉取每个章节内容
    chapters.value.length = 0
    for (const chapter of chapterList) {
      let content = ''
      try {
        const res = await fetch(`/api/chapters/${chapter.id}`)
        const data = await res.json()
        if (data.success && data.data) {
          content = data.data.content || ''
        }
      } catch (e) {
        // 忽略章节内容拉取异常，避免中断循环
      }
      chapters.value.push({
        chapterNumber: chapter.chapter_number || chapter.id || '',
        title: chapter.title || 'Unnamed Chapter',
        content,
        dbId: chapter.id
      })
      documentContents.value[chapter.chapter_number || chapter.id || ''] = content
      chapterStatuses.value[chapter.chapter_number || chapter.id || ''] = 'pending'
    }
    
    if (chapters.value.length === 0) {
      ElMessage.error('No chapters found in database, please generate and save directory first')
      return
    }
    
    ElMessage.success(`Successfully loaded ${chapters.value.length} chapters (database)`)
    console.log('----------------- Debug Info End -----------------')
  }
  
  return {
    // 状态
    chapters,
    currentChapter,
    chapterContent,
    documentContents,
    chapterStatuses,
    isGenerating,
    autoGenerating,
    currentGeneratingIndex,
    generationProgress,
    
    // 方法
    handleSelectChapter,
    initializeData
  }
}
