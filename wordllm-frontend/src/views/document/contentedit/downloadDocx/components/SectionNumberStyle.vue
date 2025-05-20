<template>
  <div class="section-number-style">
    <h3 class="section-title">
      标号样式
    </h3>
    <div class="number-options">
      <div class="number-option" :class="{ 'selected': selectedStyle === 'none' }">
        <el-radio v-model="selectedStyle" value="none">
          <div class="option-content">
            <div class="option-display">
              无
            </div>
          </div>
        </el-radio>
      </div>

      <div class="number-option" :class="{ 'selected': selectedStyle === 'chapter' }">
        <el-radio v-model="selectedStyle" value="chapter">
          <div class="option-content">
            <div class="option-display">
              <div>第一章 [标题]</div>
              <div>第一节 [标题]</div> 
              <div>一、 [标题]</div>
            </div>
          </div>
        </el-radio>
      </div>

      <div class="number-option" :class="{ 'selected': selectedStyle === 'number' }">
        <el-radio v-model="selectedStyle" value="number">
          <div class="option-content">
            <div class="option-display">
              <div>1 [标题]</div>
              <div>1.1 [标题]</div>
              <div>1.1.1 [标题]</div>
            </div>
          </div>
        </el-radio>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSectionNumberStyle } from './SectionNumberStyle.ts'

const selectedStyle = ref('chapter')
const sectionNumberState = useSectionNumberStyle()
console.log('[SectionNumberStyle] state', sectionNumberState)
</script>

<style scoped>
.section-number-style { 
  margin-bottom: 32px; 
}

.section-title {
  font-size: 16px;
  font-weight: normal;
  margin-bottom: 16px;
}

.number-options {
  display: flex;
  gap: 16px;
}

.number-option {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  flex: 1;
}

.number-option.selected {
  border-color: #409EFF;
}

.option-content {
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-display {
  font-size: 13px;
  color: #606266;
}
</style>
