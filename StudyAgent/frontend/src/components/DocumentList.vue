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
    <el-table-column label="操作" width="220">
      <template #default="{ row }">
        <el-button type="default" size="small" @click="handleView(row.id)">查看内容</el-button>
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

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="60%" top="5vh" destroy-on-close>
    <div v-loading="contentLoading" class="content-box">
      <pre v-if="documentContent" class="content-pre">{{ documentContent }}</pre>
      <el-empty v-else-if="!contentLoading" description="无法读取文档内容" />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, deleteDocument, rebuildDocument, getDocumentContent } from '../api/document'

const documents = ref([])
const loading = ref(false)
const rebuildingId = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const documentContent = ref('')
const contentLoading = ref(false)

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getDocuments()
    documents.value = res.data || []
  } finally {
    loading.value = false
  }
}

const handleView = async (id) => {
  const doc = documents.value.find((d) => d.id === id)
  dialogTitle.value = doc ? doc.filename : '文档内容'
  dialogVisible.value = true
  contentLoading.value = true
  documentContent.value = ''
  try {
    const res = await getDocumentContent(id)
    documentContent.value = res.data.content || ''
  } catch {
    documentContent.value = ''
  } finally {
    contentLoading.value = false
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

<style scoped>
.content-box {
  max-height: 65vh;
  overflow-y: auto;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 16px;
}
.content-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}
</style>
