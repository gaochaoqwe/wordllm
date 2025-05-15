<template>
  <div class="chapter-outline-tree">
    <el-tree
      ref="treeRef"
      :data="treeData"
      node-key="chapterNumber"
      :expand-on-click-node="false"
      :default-expanded-keys="defaultExpandedKeys"
      :highlight-current="true"
      @node-click="handleNodeClick"
    >
      <template #default="{ data }">
        <div class="custom-tree-node">
          <!-- 状态图标 -->
          <img 
            :src="getStatusIcon(data.status)" 
            class="status-icon" 
            :alt="data.status || 'pending'" 
          />
          <!-- 章节编号和标题 -->
          <span class="chapter-number">{{ data.chapterNumber }}</span>
          <span class="chapter-title">{{ data.title }}</span>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

import type { ElTree } from 'element-plus'

// 章节类型定义
interface Chapter {
  chapterNumber: string;
  title: string;
  content?: string;
}

// 树节点类型
interface TreeNode extends Chapter {
  children?: TreeNode[];
}

// Props和事件
const props = defineProps<{
  chapters: Chapter[],
  chapterStatuses?: Record<string, string> // 章节状态映射: chapterNumber -> status
}>()

const emit = defineEmits<{
  (e: 'select-chapter', chapter: Chapter): void
}>()

// 树引用
const treeRef = ref<InstanceType<typeof ElTree>>()

// 默认展开的节点
const defaultExpandedKeys = ref<string[]>([])

// 添加props变化的监听
watch(() => props.chapters, (newVal, oldVal) => {
  console.log('[ChapterOutlineTree] chapters prop 变化:', {
    新数量: newVal?.length || 0,
    旧数量: oldVal?.length || 0,
    样例: newVal && newVal.length > 0 ? newVal[0] : null
  })
  
  if (newVal && newVal.length > 0) {
    // 收集所有章节编号作为展开键
    const expandKeys = newVal.map(chapter => chapter.chapterNumber)
    console.log('[ChapterOutlineTree] 设置展开键:', expandKeys)
    defaultExpandedKeys.value = expandKeys
  }
}, { immediate: true })

// 将章节列表转换为树形结构
const treeData = computed(() => {
  console.log('[ChapterOutlineTree] 重新计算treeData, chapters长度:', props.chapters?.length || 0)
  // 创建章节树的映射
  const chapterMap: Record<string, TreeNode> = {}
  const result: TreeNode[] = []

  // 首先创建所有节点
  props.chapters.forEach(chapter => {
    chapterMap[chapter.chapterNumber] = {
      ...chapter,
      children: []
    }
  })

  // 然后构建树结构
  props.chapters.forEach(chapter => {
    const node = chapterMap[chapter.chapterNumber]
    
    // 判断是否有父节点
    const parts = chapter.chapterNumber.split('.')
    
    if (parts.length === 1) {
      // 一级章节，直接加入结果
      result.push(node)
    } else {
      // 非一级章节，查找父节点
      const parentParts = parts.slice(0, -1)
      const parentKey = parentParts.join('.')
      
      if (chapterMap[parentKey]) {
        if (!chapterMap[parentKey].children) {
          chapterMap[parentKey].children = []
        }
        chapterMap[parentKey].children!.push(node)
      } else {
        // 如果找不到父节点（理论上不应该发生），作为顶级节点处理
        result.push(node)
      }
    }
  })

  return result
})

// 监听章节变化，更新默认展开节点
watch(() => props.chapters, () => {
  // 默认展开第一级节点
  defaultExpandedKeys.value = treeData.value.map(node => node.chapterNumber)
}, { immediate: true })

// 处理节点点击
function handleNodeClick(data: TreeNode) {
  console.log('[ChapterOutlineTree] 节点被点击:', data)
  emit('select-chapter', {
    chapterNumber: data.chapterNumber,
    title: data.title,
    content: data.content
  })
  console.log('[ChapterOutlineTree] 已 emit select-chapter:', {
    chapterNumber: data.chapterNumber,
    title: data.title,
    content: data.content
  })
}

// 定义图片资源路径
const assetsPath = '/src/assets/';
const doneIcon = assetsPath + 'done.png';
const errorIcon = assetsPath + 'error.png';
const generatingIcon = assetsPath + 'generating.gif';
const pendingIcon = assetsPath + 'pending.png';


// 获取状态图标
function getStatusIcon(status?: string) {
  if (!status) return pendingIcon;
  switch (status) {
    case 'done':
      return doneIcon;
    case 'generating':
      return generatingIcon;
    case 'error':
      return errorIcon;
    case 'pending':
    default:
      return pendingIcon;
  }
}

// 在组件挂载后收集展开键
onMounted(() => {
  console.log('[ChapterOutlineTree] 组件挂载, 当前chapters数量:', props.chapters?.length || 0)
  console.log('[ChapterOutlineTree] 树形数据:', treeData.value)
  
  // 手动设置所有节点为展开状态
  if (props.chapters && props.chapters.length > 0) {
    const expandKeys = props.chapters.map(chapter => chapter.chapterNumber)
    console.log('[ChapterOutlineTree] 设置默认展开键:', expandKeys)
    defaultExpandedKeys.value = expandKeys
  }
  
  // 如果树尚未加载，等待下一个tick
  if (!treeRef.value && treeData.value.length > 0) {
    setTimeout(() => {
      defaultExpandedKeys.value = treeData.value.map(node => node.chapterNumber)
    }, 100)
  }
})
</script>

<style scoped>
.chapter-outline-tree {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 5px 0;
}

.chapter-number {
  min-width: 40px;
  font-weight: 500;
  color: #409eff;
}

.chapter-title {
  flex: 1;
  margin-left: 8px;
}

.chapter-status {
  margin-left: 8px;
  color: #a0a0a0;
}

.chapter-status.has-content {
  color: #67c23a;
}

.status-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}
</style>
