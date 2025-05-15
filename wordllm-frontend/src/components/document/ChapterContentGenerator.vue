<template>
  <div>
    <el-progress :percentage="progressPercent" style="margin-bottom: 16px;" />
    <div v-if="generating" class="generating-tip">
      正在生成第 {{ currentIdx + 1 }}/{{ chapters.length }} 章：{{ chapters[currentIdx]?.title }}
    </div>
    <ChapterContentList :chapter-contents="chapterStates" />
    <div v-if="errorMsg" class="error-msg">
      {{ errorMsg }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ChapterContentList from './ChapterContentList.vue'
import { generateChapterContent } from '@/views/document/contentedit/services/documentService'

const props = defineProps({
  templateId: { type: [String, Number], required: true },
  chapters: { type: Array, required: true }
})

// 日志调试信息
console.log('ChapterContentGenerator 初始化, props:', {
  templateId: props.templateId,
  chaptersLength: props.chapters?.length || 0,
  chaptersData: props.chapters
})

// 当前章节索引 - 用于显示生成进度
const currentIdx = ref(0)

// 初始化章节状态 - 为每章添加status和content字段
const chapterStates = ref((props.chapters || []).map(chap => ({
  ...chap,
  content: '',
  status: 'pending' // 'pending' | 'generating' | 'done' | 'error'
})))

const generating = ref(false)
const errorMsg = ref('')

// 计算进度百分比
const progressPercent = computed(() => {
  if (!chapterStates.value.length) return 0
  const doneCount = chapterStates.value.filter(c => c.status === 'done').length
  return Math.round((doneCount / chapterStates.value.length) * 100)
})

// 开始生成章节内容
async function startGenerate() {
  console.log('开始生成章节内容, 章节数:', chapterStates.value.length)
  
  // 边界检查
  if (!chapterStates.value.length) {
    errorMsg.value = '无章节数据可生成'
    ElMessage.warning(errorMsg.value)
    return
  }
  
  if (!props.templateId) {
    errorMsg.value = '缺少模板ID，无法生成章节内容'
    ElMessage.warning(errorMsg.value)
    return
  }
  
  generating.value = true
  errorMsg.value = ''
  
  for (let i = 0; i < chapterStates.value.length; i++) {
    currentIdx.value = i
    const chapter = chapterStates.value[i]
    
    console.log(`开始生成第${i+1}章: ${chapter.title}`, chapter)
    chapter.status = 'generating'
    
    try {
      console.log('调用API生成章节内容, 参数:', {
        templateId: props.templateId,
        chapterNumber: chapter.chapterNumber,
        title: chapter.title
      })
      
      const res = await generateChapterContent(props.templateId, chapter)
      console.log(`第${i+1}章生成成功:`, res)
      
      chapter.content = res.content || ''
      chapter.status = 'done'
    } catch (e) {
      console.error(`第${i+1}章生成失败:`, e)
      chapter.status = 'error'
      chapter.content = ''
      errorMsg.value = `第${i+1}章生成失败：${e.message || e}`
      ElMessage.error(errorMsg.value)
      break
    }
  }
  
  generating.value = false
  console.log('所有章节生成完成')
}

onMounted(() => {
  console.log('ChapterContentGenerator组件已挂载，准备生成内容')
  startGenerate()
})

</script>

<style scoped>
.generating-tip { color: #409eff; margin-bottom: 12px; }
.error-msg { color: #f56c6c; margin-top: 16px; }
</style>
