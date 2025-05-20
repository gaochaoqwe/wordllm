<template>
  <div class="page-format">
    <h3 class="section-title">
      页面格式
    </h3>
    <div class="margin-settings">
      <div class="margin-row">
        <div class="margin-item">
          <span class="required">
            *
          </span>
          <label>上边距：</label>
          <el-input-number
            v-model="margins.top"
            :min="0"
            :precision="2"
            :step="0.5"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            cm
          </span>
        </div>
        <div class="margin-item">
          <span class="required">
            *
          </span>
          <label>下边距：</label>
          <el-input-number
            v-model="margins.bottom"
            :min="0"
            :precision="2"
            :step="0.5"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            cm
          </span>
        </div>
      </div>
      
      <div class="margin-row">
        <div class="margin-item">
          <span class="required">
            *
          </span>
          <label>左边距：</label>
          <el-input-number
            v-model="margins.left"
            :min="0"
            :precision="2"
            :step="0.5"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            cm
          </span>
        </div>
        <div class="margin-item">
          <span class="required">
            *
          </span>
          <label>右边距：</label>
          <el-input-number
            v-model="margins.right"
            :min="0"
            :precision="2"
            :step="0.5"
            size="small"
            controls-position="right"
          />
          <span class="unit">
            cm
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { usePageFormat } from './PageFormat.ts'

const margins = reactive({
  top: 2.54,
  bottom: 2.54,
  left: 3.18,
  right: 3.18
})

const pageFormatState = usePageFormat()
console.log('[PageFormat] state', pageFormatState)
</script>

<style scoped>
.page-format { 
  margin-bottom: 32px; 
}

.section-title {
  font-size: 16px;
  font-weight: normal;
  margin-bottom: 16px;
}

.margin-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.margin-row {
  display: flex;
  gap: 24px;
}

.margin-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #f56c6c;
  margin-right: 2px;
}

.unit {
  color: #606266;
  margin-left: 2px;
}
</style>
