<template>
  <div class="project-container">
    <div class="project-header">
      <el-input
        v-model="searchTitle"
        placeholder="搜索项目标题"
        class="search-input"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><SearchIcon /></el-icon>
        </template>
      </el-input>
      
      <el-button 
        type="primary" 
        @click="showCreateDialog"
      >
        <el-icon><PlusIcon /></el-icon>
        新建项目
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="projects"
      style="width: 100%"
      highlight-current-row
      @current-change="handleRowClick"
    >
      <!-- 项目名称列 -->
      <el-table-column 
        prop="project_name" 
        label="项目名称" 
        min-width="200"
      >
        <template #default="{ row }">
          {{ row.project_name || row.title || '无名项目' }}
        </template>
      </el-table-column>
      
      <!-- 模板名称列 -->
      <el-table-column 
        prop="template_name" 
        label="模板名称" 
        min-width="200"
      >
        <template #default="{ row }">
          {{ row.template_name || row.title || '无名模板' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="created_at" 
        label="创建时间" 
        width="180"
      >
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column 
        label="操作" 
        width="240" 
        fixed="right"
      >
        <template #default="{ row }">
          <el-button-group>
            <el-button 
              size="small" 
              type="primary" 
              @click="handleEdit(row)"
            >
              <el-icon><EditIcon /></el-icon>编辑内容
            </el-button>
            <el-button 
              size="small" 
              @click="handleView(row)"
            >
              编辑目录
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 新建项目对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建项目"
      width="600px"
      align-center
      destroy-on-close
    >
      <div class="create-options">
        <div 
          class="option-card" 
          @click="handleCreateFromTemplate"
        >
          <div class="option-icon">
            <img src="/src/assets/template-icon.png" alt="模板图标" />
          </div>
          <div class="option-title">
            根据模板创建
          </div>
        </div>
        
        <div 
          class="option-card" 
          @click="handleCreateFromFile"
        >
          <div class="option-icon">
            <img src="/src/assets/file-icon.png" alt="文件图标" />
          </div>
          <div class="option-title">
            根据已有文件创建
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Plus as PlusIcon,
} from '@element-plus/icons-vue'
import { fetchProjects, type Project } from '@/views/project/services/projectService';

const router = useRouter()

// 响应式数据
const searchTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const projects = ref<Project[]>([])
const total = ref(0)
const selectedProject = ref<Project | null>(null)
const createDialogVisible = ref(false)

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

// 加载项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const response = await fetchProjects(currentPage.value, pageSize.value, searchTitle.value);
    if (response.success) {
      projects.value = response.data;
      total.value = response.total;
    } else {
      // Handle business error if success is false but no exception was thrown
      ElMessage.error(response.message || '加载项目列表失败');
      projects.value = []; // Clear projects on error
      total.value = 0;
    }
  } catch (error) {
    console.error('Failed to load projects:', error);
    ElMessage.error('加载项目列表时发生网络或服务器错误');
    projects.value = []; // Clear projects on error
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadProjects()
}

// 处理行点击
const handleRowClick = (row: Project) => {
  selectedProject.value = row
}

// 显示创建项目对话框
const showCreateDialog = () => {
  createDialogVisible.value = true
}

// 根据模板创建项目
const handleCreateFromTemplate = () => {
  createDialogVisible.value = false
  setTimeout(() => {
    router.push('/projects/create-by-template')
  }, 300)
}

// 根据已有文件创建项目
const handleCreateFromFile = () => {
  ElMessage.info('根据已有文件创建项目功能待实现')
  createDialogVisible.value = false
}

// 编辑项目 - 跳转到文档编辑器页面
const handleEdit = (project: Project) => {
  console.log('跳转到编辑项目页面:', project.id)
  
  // 使用路由跳转到文档编辑器页面，并传递项目ID作为查询参数
  router.push({
    path: '/document/editor',
    query: {
      projectId: project.id.toString()
    }
  })
}

// 编辑目录
const handleView = (project: Project) => {
  console.log('编辑项目目录:', project.id)
  
  // 跳转到大纲结果页面
  router.push({
    path: '/document/outline-result',
    query: {
      projectId: project.id.toString(),
      templateId: project.template_id ? project.template_id.toString() : null
    }
  })
}

// 删除项目
const handleDelete = async (project: Project) => {
  console.log('删除项目:', project.id)
  ElMessage.info(`删除项目: ${project.project_name || project.title}`)
}

// 处理分页
const handleSizeChange = (size) => {
  pageSize.value = size
  loadProjects()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadProjects()
}

// 初始化加载
onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  flex: 1;
  overflow: auto;
}

:deep(.el-button-group .el-button--link) {
  border: none;
  padding: 0 8px;
}

/* 创建选项卡片样式 */
.create-options {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 0;
}

.option-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  border-radius: 8px;
  border: 1px solid #e6e6e6;
  transition: all 0.3s;
  cursor: pointer;
}

.option-card:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.option-icon {
  width: 80px;
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f7ff;
  border-radius: 50%;
  margin-bottom: 15px;
}

.option-icon img {
  width: 40px;
  height: 40px;
}

.option-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.option-desc {
  font-size: 13px;
  color: #909399;
}
</style>
