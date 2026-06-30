<template>
  <div>
    <h2>知识库管理</h2>
    <el-card shadow="never" style="margin-bottom: 20px">
      <DocumentUpload @uploaded="refreshList" />
    </el-card>
    <el-card shadow="never">
      <DocumentList ref="listRef" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DocumentUpload from '../components/DocumentUpload.vue'
import DocumentList from '../components/DocumentList.vue'

const listRef = ref(null)

const refreshList = () => {
  listRef.value?.fetchList()
}
</script>

<style scoped>
h2 {
  margin-bottom: 16px;
}
</style>
