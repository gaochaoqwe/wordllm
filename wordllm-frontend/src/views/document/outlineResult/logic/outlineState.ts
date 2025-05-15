import { reactive } from 'vue'
import { Chapter } from './types'
import type { RouteLocationNormalizedLoaded } from 'vue-router'

// 导出状态 - 使用reactive创建一个响应式对象
export const outlineState = reactive({
  templateTitle: '模板标题示例',
  inputFileName: '输入文件.docx',
  templateId: null as number|null,
  inputFilePath: null as string|null,
  templatePath: '', // 添加模板文件路径
  allChecked: false,
  chapters: [] as Chapter[],
  projectId: null as string|null,
  activeTab: 'template',
  hasGeneratedSubchapters: false,
  isGeneratingDocument: false
})

// 初始化项目和模板数据
export async function initializeFromRoute(route: RouteLocationNormalizedLoaded) {
  console.log('[DEBUG-ROUTE] 接收到的route对象:', route?.query)
  const projectIdParam = route?.query?.projectId
  const templateIdParam = route?.query?.templateId
  const inputFileNameParam = route?.query?.inputFileName
  
  if (!projectIdParam) {
    throw new Error('未找到项目ID，无法加载大纲')
  }
  
  // 直接修改reactive对象的属性
  outlineState.projectId = projectIdParam as string
  if (inputFileNameParam) outlineState.inputFileName = inputFileNameParam as string
  if (templateIdParam) outlineState.templateId = Number(templateIdParam)
  
  return {
    projectId: outlineState.projectId,
    templateId: outlineState.templateId,
    inputFileName: outlineState.inputFileName
  }
}

// 加载默认章节数据
export function loadDefaultChapters() {
  outlineState.chapters = [
    { chapterNumber: '1', title: '引言' },
    { chapterNumber: '2', title: '研究方法' },
    { chapterNumber: '3', title: '实验设计' },
    { chapterNumber: '4', title: '数据分析' },
    { chapterNumber: '5', title: '结论与展望' }
  ]
  console.log('[DEBUG-STATE] 默认章节已加载:', outlineState.chapters)
}

// 添加章节
export function addChapter() {
  const nextChapterNumber = String(outlineState.chapters.length + 1)
  outlineState.chapters.push({
    chapterNumber: nextChapterNumber,
    title: `新章节 ${nextChapterNumber}`
  })
  console.log('[DEBUG-STATE] 添加新章节，当前章节总数:', outlineState.chapters.length)
}

// 移除指定索引的章节
export function removeChapter(idx: number) {
  if (idx >= 0 && idx < outlineState.chapters.length) {
    outlineState.chapters.splice(idx, 1)
    console.log('[DEBUG-STATE] 删除章节，当前章节总数:', outlineState.chapters.length)
  }
}

// 移除指定节点的章节
export function removeChapterByNode(data: { chapterNumber: string }) {
  // 根据 chapterNumber 属性查找节点
  const idx = outlineState.chapters.findIndex(ch => ch.chapterNumber === data.chapterNumber)
  console.log('[DEBUG-STATE] 根据节点删除章节, chapterNumber:', data.chapterNumber, '找到索引:', idx)
  removeChapter(idx)
}

// 在指定索引位置添加需求
export function addRequirement(idx: number) {
  // 具体实现取决于需求的数据模型
  if (idx >= 0 && idx < outlineState.chapters.length) {
    // 例如，可以向章节对象添加requirement属性
    outlineState.chapters[idx].requirement = outlineState.chapters[idx].requirement || ''
    console.log('[DEBUG-STATE] 在索引', idx, '处添加需求')
  }
}

// 为指定节点添加需求
export function addRequirementByNode(data: { chapterNumber: string }) {
  // 根据节点查找索引
  const idx = outlineState.chapters.findIndex(ch => ch.chapterNumber === data.chapterNumber)
  console.log('[DEBUG-STATE] 根据节点添加需求, chapterNumber:', data.chapterNumber, '找到索引:', idx)
  if (idx !== -1) {
    addRequirement(idx)
  }
}
