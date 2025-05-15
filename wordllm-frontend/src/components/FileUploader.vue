<template>
  <div class="file-uploader">
    <input
      ref="fileInput"
      type="file"
      style="display: none"
      :accept="accept"
      @change="handleFileUpload"
    />
    <el-button :type="buttonType" @click="triggerFileInput">
      {{ buttonText }}
    </el-button>
    
    <div v-if="uploadedFile" class="file-info">
      <p>已上传文件: {{ uploadedFile.name }}</p>
      <p>文件大小: {{ formatFileSize(uploadedFile.size) }}</p>
      <div v-if="showActions" class="actions">
        <el-button 
          v-if="canDownload" 
          type="success" 
          size="small"
          @click="downloadFile"
        >
          下载文件
        </el-button>
        <el-button type="danger" size="small" @click="clearFile">
          清除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineEmits, defineProps, defineExpose } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  // 接受的文件类型
  accept: {
    type: String,
    default: '.docx,.doc,.pdf'
  },
  // 按钮文本
  buttonText: {
    type: String,
    default: '上传文件'
  },
  // 按钮类型
  buttonType: {
    type: String,
    default: 'primary'
  },
  // 上传API地址
  uploadUrl: {
    type: String,
    default: ''
  },
  // 最大文件大小(MB)
  maxSize: {
    type: Number,
    default: 10
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: true
  },
  // 是否可以下载
  canDownload: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['file-selected', 'file-uploaded', 'file-removed', 'upload-error'])

const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFile = ref<File | null>(null)
const uploadedFileUrl = ref<string | null>(null)

// 最大文件大小 (转换为字节)
const MAX_FILE_SIZE = computed(() => props.maxSize * 1024 * 1024)

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const validateFile = (file: File) => {
  // 验证文件大小
  if (file.size > MAX_FILE_SIZE.value) {
    ElMessage.error(`文件大小不能超过${props.maxSize}MB`)
    return false
  }

  return true
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 前端验证文件
  if (!validateFile(file)) {
    // 清空文件输入
    target.value = ''
    return
  }

  uploadedFile.value = file
  emit('file-selected', file)
  
  // 如果提供了上传URL，则自动上传
  if (props.uploadUrl) {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(props.uploadUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      uploadedFileUrl.value = response.data.fileUrl || response.data.url || ''
      emit('file-uploaded', response.data)
      ElMessage.success('文件上传成功')
    } catch (error: unknown) {
      emit('upload-error', error)
      // 使用类型断言处理 unknown 类型
      const err = error as { response?: { data?: { message?: string } } }
      ElMessage.error(err.response?.data?.message || '文件上传失败')
      console.error(error)
    }
  }
}

const downloadFile = async () => {
  if (!uploadedFileUrl.value && !uploadedFile.value) {
    ElMessage.error('没有可下载的文件')
    return
  }
  
  try {
    if (uploadedFileUrl.value) {
      // 从服务器下载文件
      const response = await axios.get(uploadedFileUrl.value, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', uploadedFile.value?.name || 'download')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } else if (uploadedFile.value) {
      // 直接下载本地文件
      const url = window.URL.createObjectURL(uploadedFile.value)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', uploadedFile.value.name)
      document.body.appendChild(link)
      link.click()
      link.remove()
    }
  } catch (error) {
    ElMessage.error('文件下载失败')
    console.error(error)
  }
}

// 格式化文件大小
const formatFileSize = (size?: number) => {
  if (!size) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  let fileSize = size
  while (fileSize >= 1024 && index < units.length - 1) {
    fileSize /= 1024
    index++
  }
  return `${fileSize.toFixed(2)} ${units[index]}`
}

// 清除文件
const clearFile = () => {
  uploadedFile.value = null
  uploadedFileUrl.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('file-removed')
}

// 设置文件 - 用于外部设置
const setFile = (file: File, fileUrl?: string) => {
  uploadedFile.value = file
  if (fileUrl) {
    uploadedFileUrl.value = fileUrl
  }
}

// 获取当前文件
const getFile = () => {
  return uploadedFile.value
}

// 获取文件URL
const getFileUrl = () => {
  return uploadedFileUrl.value
}

// 暴露方法给父组件
defineExpose({
  clearFile,
  setFile,
  getFile,
  getFileUrl
});
</script>

<!-- 添加显式的默认导出供类型系统识别 -->
<script lang="ts">
export default {
  name: 'FileUploader'
}
</script>

<style scoped>
.file-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px;
}

.file-info {
  margin-top: 10px;
  text-align: center;
}
</style>
