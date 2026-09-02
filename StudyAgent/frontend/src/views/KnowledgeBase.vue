<template>
  <div class="knowledge-page">
    <div class="page-header">
      <div>
        <h2>知识库管理</h2>
      </div>
    </div>

    <!-- 上传区域 -->
    <el-card shadow="never" class="upload-card">
      <DocumentUpload @uploaded="refreshList" @queue-change="handleQueueChange" />
    </el-card>

    <!-- 数据统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>

        <div class="stat-info">
          <span class="stat-label">文档总数</span>
          <div class="stat-value">
            {{ totalCount }}
            <span>个</span>
          </div>
          <div class="stat-desc">
            累计上传
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><CircleCheck /></el-icon>
        </div>

        <div class="stat-info">
          <span class="stat-label">已处理</span>
          <div class="stat-value">
            {{ stats.processed }}
            <span>个</span>
          </div>
          <div class="stat-desc">
            占比 {{ processedPercent }}
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Loading /></el-icon>
        </div>

        <div class="stat-info">
          <span class="stat-label">处理中</span>
          <div class="stat-value">
            {{ stats.processing }}
            <span>个</span>
          </div>
          <div class="stat-desc">
            占比 {{ processingPercent }}
          </div>
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <el-card shadow="never" class="list-card">
      <div class="list-header">
        <div>
          <h3>文件列表</h3>
        </div>
      </div>

      <DocumentList
        ref="listRef"
        @changed="fetchStats"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Document,
  CircleCheck,
  Loading
} from '@element-plus/icons-vue'

import DocumentUpload from '../components/DocumentUpload.vue'
import DocumentList from '../components/DocumentList.vue'
import { getDocuments } from '../api/document'

const listRef = ref(null)

const stats = reactive({
  processed: 0,
  processing: 0,
})

const totalCount = computed(() => stats.processed + stats.processing)

const processedPercent = computed(() => {
  if (!totalCount.value) return '0%'
  return ((stats.processed / totalCount.value) * 100).toFixed(1) + '%'
})

const processingPercent = computed(() => {
  if (!totalCount.value) return '0%'
  return ((stats.processing / totalCount.value) * 100).toFixed(1) + '%'
})

const fetchStats = async () => {
  try {
    const res = await getDocuments()
    const docs = res.data || []
    stats.processed = docs.filter((d) => d.status === 'ready').length
  } catch {
    // 后端未就绪时保持原值
  }
}

const handleQueueChange = (n) => {
  stats.processing = n
}

const refreshList = () => {
  listRef.value?.fetchList()
  fetchStats()
}

onMounted(fetchStats)
</script>

<style scoped>
.knowledge-page {
  width: 100%;
  box-sizing: border-box;
  padding: 4px 8px 24px;
}

.page-header {
  margin-bottom: 22px;
}

.page-header h2 {
  margin-bottom: 16px;
  text-align: center;
  font-family: "Microsoft YaHei","微软雅黑",sans-serif;
  font-size: 24px;
  font-weight: 500;
}

.page-header p {
  margin: -8px 0 0;
  color: #7b8494;
  font-size: 13px;
  text-align: center;
}

.upload-card {
  margin-bottom: 20px;
  border: 1px solid #edf0f5;
  border-radius: 16px;
  background: #ffffff;
  min-height: 280px; /* 添加最小高度，拉长上传区域 */
}

.upload-card :deep(.el-card__body) {
  padding: 20px;
}

.upload-card :deep(.el-upload-dragger) {
  min-height: 200px; /* 拉长虚线框 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  min-height: 108px;
  padding: 18px 20px;
  box-sizing: border-box;

  display: flex;
  align-items: center;
  gap: 15px;

  background: #ffffff;
  border: 1px solid #edf0f5;
  border-radius: 14px;

  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(30, 50, 90, 0.06);
}

/* 图标 */

.stat-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 50%;
  font-size: 23px;
}

.stat-icon.blue {
  color: #5b7ff1;
  background: #edf2ff;
}

.stat-icon.green {
  color: #49b98b;
  background: #eaf8f2;
}

.stat-icon.orange {
  color: #f18b4f;
  background: #fff0e7;
}

.stat-icon.purple {
  color: #9a6be6;
  background: #f2eaff;
}

/* 数据 */

.stat-info {
  min-width: 0;
}

.stat-label {
  display: block;
  margin-bottom: 5px;
  color: #7c8493;
  font-size: 13px;
}

.stat-value {
  color: #202938;
  font-size: 23px;
  font-weight: 600;
  line-height: 1.25;
}

.stat-value span {
  margin-left: 3px;
  color: #656e7d;
  font-size: 12px;
  font-weight: 400;
}

.stat-desc {
  margin-top: 5px;
  color: #8c94a2;
  font-size: 11px;
}

.stat-desc strong {
  color: #48a77e;
  font-weight: 500;
}

.list-card {
  border: 1px solid #edf0f5;
  border-radius: 16px;
  background: #ffffff;
}

.list-card :deep(.el-card__body) {
  padding: 20px;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 14px;
}

.list-header h3 {
  margin: 0;
  color: #202938;
  font-size: 16px;
  font-weight: 600;
}

@media screen and (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media screen and (max-width: 700px) {
  .knowledge-page {
    padding: 4px 4px 20px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header h2 {
  font-size: 22px;
  }
}
</style>
