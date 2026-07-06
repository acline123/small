<template>
  <div class="graph-page">
    <div class="graph-header">
      <h2>知识图谱</h2>
      <div class="graph-controls">
        <el-select
          v-model="selectedDocId"
          placeholder="全部文档"
          clearable
          style="width: 260px"
          @change="fetchGraph"
        >
          <el-option
            v-for="doc in documents"
            :key="doc.id"
            :label="doc.filename"
            :value="doc.id"
          />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchGraph">刷新</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-num">{{ stats.nodes }}</div>
          <div class="stat-label">实体节点</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-num">{{ stats.edges }}</div>
          <div class="stat-label">关系边</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-num">{{ selectedDocId ? 1 : documents.length }}</div>
          <div class="stat-label">覆盖文档</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="graph-card" v-loading="loading">
      <div v-if="!stats.nodes" class="empty-tip">
        暂无知识图谱数据，请先上传文档并等待知识库构建完成
      </div>
      <div ref="chartRef" class="chart-container" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getGraph } from '../api/graph'
import { getDocuments } from '../api/document'

const TYPE_COLORS = {
  概念: '#409eff',
  技术: '#67c23a',
  方法: '#e6a23c',
  人物: '#f56c6c',
  组织: '#909399',
}

const chartRef = ref(null)
const loading = ref(false)
const documents = ref([])
const selectedDocId = ref(null)
const stats = ref({ nodes: 0, edges: 0 })
let chart = null

const renderChart = (nodes, edges) => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const echartsNodes = nodes.map((n) => ({
    id: String(n.id),
    name: n.name,
    symbolSize: 40,
    category: n.type,
    itemStyle: { color: TYPE_COLORS[n.type] || '#409eff' },
  }))

  const categories = [...new Set(nodes.map((n) => n.type))].map((t) => ({ name: t }))

  const echartsEdges = edges.map((e) => ({
    source: String(e.source),
    target: String(e.target),
    label: { show: true, formatter: e.type, fontSize: 10 },
  }))

  chart.setOption({
    tooltip: {},
    legend: [{ data: categories.map((c) => c.name), bottom: 0 }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        categories,
        data: echartsNodes,
        links: echartsEdges,
        label: { show: true, position: 'right', fontSize: 12 },
        force: { repulsion: 300, edgeLength: [80, 160] },
        lineStyle: { color: '#aaa', curveness: 0.1 },
        emphasis: { focus: 'adjacency' },
      },
    ],
  })
}

const fetchGraph = async () => {
  loading.value = true
  try {
    const res = await getGraph(selectedDocId.value || undefined)
    const data = res.data || {}
    const nodes = data.nodes || []
    const edges = data.edges || []
    stats.value = { nodes: nodes.length, edges: edges.length }
    await nextTick()
    if (nodes.length) {
      renderChart(nodes, edges)
    } else if (chart) {
      chart.clear()
    }
  } finally {
    loading.value = false
  }
}

const handleResize = () => chart?.resize()

onMounted(async () => {
  const res = await getDocuments()
  documents.value = res.data || []
  await fetchGraph()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.graph-header h2 {
  margin: 0;
}
.graph-controls {
  display: flex;
  gap: 12px;
}
.stats-row {
  margin-bottom: 16px;
}
.stat-num {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  color: #909399;
  margin-top: 4px;
}
.graph-card {
  min-height: 500px;
}
.chart-container {
  width: 100%;
  height: 520px;
}
.empty-tip {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
</style>
