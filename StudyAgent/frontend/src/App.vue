<template>
  <el-container class="layout">
    <el-aside width="280px" class="aside">
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
        <el-menu-item index="/exercise">
          <el-icon><EditPen /></el-icon>
          <span>智能习题</span>
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
  background: white;
  color: black;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 26px;
  font-weight: bold;
  color: black;
  border-bottom: 1px solid white;
}
.aside :deep(.el-menu) {
  border-right: none;
  background: white;
}
.aside :deep(.el-menu-item) {
  color: black;
  height: 75px;
  font-size: 26px;
  font-family: "Comic Sans MS","Comic Sans",cursive;
}
.aside :deep(.el-menu-item.is-active) {
  background: #263445 !important;
  color: rgba(255, 255, 255, 0.6);
}
.main {
  padding: 20px;
}
</style>
