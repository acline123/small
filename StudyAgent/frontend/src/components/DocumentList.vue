<template>
  <el-table :data="documents" stripe v-loading="loading">
    <el-table-column prop="filename" label="文件名" min-width="200" />
    <el-table-column prop="file_type" label="类型" width="80" />
    <el-table-column prop="chunk_count" label="文本块数" width="100" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="row.status === 'ready' ? 'success' : row.status === 'error' ? 'danger' : 'warning'">
          {{ row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="上传时间" width="180" />
    <el-table-column label="操作" width="160">
      <template #default="{ row }">
        <el-button
          v-if="row.status === 'error'"
          type="primary"
          size="small"
          :loading="rebuildingId === row.id"
          @click="handleRebuild(row.id)"
        >
          重试
        </el-button>
        <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, deleteDocument, rebuildDocument } from '../api/document'

const documents = ref([])
const loading = ref(false)
const rebuildingId = ref(null)

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getDocuments()
    documents.value = res.data || []
  } finally {
    loading.value = false
  }
}

const handleRebuild = async (id) => {
  rebuildingId.value = id
  try {
    await rebuildDocument(id)
    ElMessage.success('重建成功')
    fetchList()
  } finally {
    rebuildingId.value = null
  }
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除该文档及其向量数据？', '提示', { type: 'warning' })
  await deleteDocument(id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(fetchList)
defineExpose({ fetchList })
</script>
