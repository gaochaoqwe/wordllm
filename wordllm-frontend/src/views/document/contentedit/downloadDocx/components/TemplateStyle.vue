<template>
  <div class="template-style">
    <h3 class="section-title">
      模板样式
    </h3>
    
    <div class="template-options">
      <div 
        v-for="(template, index) in templates" 
        :key="index"
        class="template-option"
        :class="{ 'selected': selectedTemplate === template.id }"
        @click="selectTemplate(template.id)"
      >
        <el-radio v-model="selectedTemplate" :value="template.id">
          <div class="template-preview">
            <img :src="template.image" :alt="template.name" class="preview-image" />
          </div>
        </el-radio>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTemplateStyle } from './TemplateStyle.ts'

// 导入模板图片
import first from '@/assets/template/first.png'
import second from '@/assets/template/second.png'
import third from '@/assets/template/third.png'
import forth from '@/assets/template/forth.png'

// 模板数据
const templates = [
  {
    id: 1,
    name: '简洁白色',
    image: first
  },
  {
    id: 2,
    name: '蓝色边框',
    image: second
  },
  {
    id: 3,
    name: '红色边框',
    image: third
  },
  {
    id: 4,
    name: '绿色边框',
    image: forth
  }
]

const selectedTemplate = ref(1)

function selectTemplate(id: number) {
  selectedTemplate.value = id
}

const templateStyleState = useTemplateStyle()
console.log('[TemplateStyle] state', templateStyleState)
</script>

<style scoped>
.template-style { 
  margin-bottom: 32px; 
}

.section-title {
  font-size: 16px;
  font-weight: normal;
  margin-bottom: 16px;
}

.template-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.template-option {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-option.selected {
  border-color: #409EFF;
}

.template-preview {
  width: 120px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
