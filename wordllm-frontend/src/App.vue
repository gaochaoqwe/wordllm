<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu
        router
        :default-active="$route.path"
        class="el-menu-vertical">
        <el-menu-item index="/projects">
          <el-icon><FolderIcon /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><DocumentIcon /></el-icon>
          <span>模板管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <h2>WordLLM 智能文档处理系统</h2>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { Document as DocumentIcon, Folder as FolderIcon } from '@element-plus/icons-vue'
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.el-menu {
  border-right: none;
}

.el-menu-vertical {
  height: 100%;
  background-color: #304156;
}

.el-menu-item {
  color: #fff;
}

.el-menu-item.is-active {
  background-color: #263445;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
