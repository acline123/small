<template>
  <div>
    <h2>文档摘要</h2>
    <el-card shadow="never">
      <el-form inline>
        <el-form-item label="选择文档">
          <el-select v-model="selectedId" placeholder="请选择文档" style="width: 320px">
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.filename"
              :value="doc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSummary">生成摘要</el-button>
        </el-form-item>
      </el-form>

      <el-divider v-if="summary" />

      <div v-if="summary" class="summary-box">
        <h3>{{ summaryTitle }}</h3>
        <p>{{ summary }}</p>
      </div>
      <el-empty v-else description="选择文档后点击生成摘要" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDocuments } from '../api/document'
import { generateSummary } from '../api/summary'

const documents = ref([])
const selectedId = ref(null)
const summary = ref('')
const summaryTitle = ref('')
const loading = ref(false)

onMounted(async () => {
  const res = await getDocuments()
  documents.value = res.data || []
})

const handleSummary = async () => {
  if (!selectedId.value) {
    ElMessage.warning('请先选择文档')
    return
  }
  loading.value = true
  summary.value = ''
  try {
    const res = await generateSummary(selectedId.value)
    summary.value = res.data.summary
    summaryTitle.value = res.data.filename
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
h2 {
  margin-bottom: 16px;
}
.summary-box {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  line-height: 1.8;
}
.summary-box h3 {
  margin-bottom: 12px;
  color: #303133;
}
</style>
