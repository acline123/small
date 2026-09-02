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
        <div class="markdown-body" v-html="renderedSummary" />
      </div>
      <el-empty v-else description="选择文档后点击生成摘要" />
    </el-card>
  </div>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import {ElMessage} from 'element-plus'
import {marked} from 'marked'
import {getDocuments} from '../api/document'
import {generateSummary} from '../api/summary'

const documents = ref([])
const selectedId = ref(null)
const summary = ref('')
const summaryTitle = ref('')
const loading = ref(false)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderedSummary = computed(() => {
  if (!summary.value) return ''
  return marked(summary.value)
})

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
  text-align: center;
  font-family: "Microsoft YaHei","微软雅黑",sans-serif;
  font-size: 24px;
  font-weight: 500;
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

/* Markdown 渲染样式 */
.markdown-body {
  line-height: 1.8;
  color: #303133;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.markdown-body :deep(h1) {
  font-size: 24px;
}

.markdown-body :deep(h2) {
  font-size: 20px;
}

.markdown-body :deep(h3) {
  font-size: 18px;
}

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1a1a1a;
}

.markdown-body :deep(code) {
  background: #e8e8e8;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
}

.markdown-body :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 16px;
  margin: 12px 0;
  color: #606266;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}
</style>
