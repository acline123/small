<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">StudyAgent</div>
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/knowledge">
          <el-icon><FolderOpened /></el-icon>
          <span>知识库管理</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </el-menu-item>
        <el-menu-item index="/summary">
          <el-icon><Document /></el-icon>
          <span>文档摘要</span>
        </el-menu-item>
        <el-menu-item index="/graph">
          <el-icon><Share /></el-icon>
          <span>知识图谱</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.aside {
  background: #304156;
  color: #fff;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #3d4f66;
}
.aside :deep(.el-menu) {
  border-right: none;
  background: #304156;
}
.aside :deep(.el-menu-item) {
  color: #bfcbd9;
}
.aside :deep(.el-menu-item.is-active) {
  background: #263445 !important;
  color: #409eff;
}
.main {
  padding: 20px;
}
</style>
