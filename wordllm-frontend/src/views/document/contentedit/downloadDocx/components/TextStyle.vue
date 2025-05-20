<template>
  <div class="text-style">
    <h3 class="section-title">
      正文格式
    </h3>
    
    <div class="text-settings">
      <div class="setting-row">
        <div class="setting-item">
          <span class="required">
            *
          </span>
          <label>字体：</label>
          <el-select
            v-model="settings.fontFamily"
            size="small"
            class="select-width"
          >
            <el-option value="仅宋体" label="仅宋体" />
            <el-option value="黑体" label="黑体" />
            <el-option value="微软雅黑" label="微软雅黑" />
          </el-select>
        </div>
        
        <div class="setting-item">
          <span class="required">
            *
          </span>
          <label>字号：</label>
          <el-select
            v-model="settings.fontSize"
            size="small"
            class="select-width"
          >
            <el-option value="小三" label="小三" />
            <el-option value="小四" label="小四" />
            <el-option value="四号" label="四号" />
          </el-select>
        </div>
      </div>
      
      <div class="setting-row">
        <div class="setting-item full-width">
          <span class="required">
            *
          </span>
          <label>对齐：</label>
          <div class="align-options">
            <el-radio-group v-model="settings.alignment">
              <el-radio-button value="左对齐">
                左对齐
              </el-radio-button>
              <el-radio-button value="居中">
                居中
              </el-radio-button>
              <el-radio-button value="右对齐">
                右对齐
              </el-radio-button>
            </el-radio-group>
            
            <div class="bold-option">
              <span class="required">
                *
              </span>
              <label>加粗：</label>
              <el-checkbox v-model="settings.bold" />
              <span v-if="settings.bold">加粗</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="setting-row">
        <div class="setting-item">
          <span class="required">
            *
          </span>
          <label>首行缩进：</label>
          <el-input-number
            v-model="settings.firstLineIndent"
            :min="0"
            :precision="0"
            :step="1"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            字符
          </span>
        </div>
        
        <div class="setting-item">
          <span class="required">
            *
          </span>
          <label>行间距：</label>
          <el-input-number
            v-model="settings.lineSpacing"
            :min="0"
            :precision="0"
            :step="1"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            磅
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useTextStyle } from './TextStyle.ts'

const settings = reactive({
  fontFamily: '仅宋体',
  fontSize: '小四',
  alignment: '左对齐',
  bold: false,
  firstLineIndent: 2,
  lineSpacing: 24
})

const textStyleState = useTextStyle()
console.log('[TextStyle] state', textStyleState)
</script>

<style scoped>
.text-style { 
  margin-bottom: 32px; 
}

.section-title {
  font-size: 16px;
  font-weight: normal;
  margin-bottom: 16px;
}

.text-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-row {
  display: flex;
  gap: 24px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.full-width {
  width: 100%;
}

.required {
  color: #f56c6c;
  margin-right: 2px;
}

.unit {
  color: #606266;
  margin-left: 2px;
}

.select-width {
  width: 100px;
}

.align-options {
  display: flex;
  align-items: center;
  gap: 30px;
}

.bold-option {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
