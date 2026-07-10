<template>
  <div class="thinking-progress">
    <div class="thinking-header">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>AI 正在思考...</span>
      <span class="elapsed-time">{{ elapsed }} 秒</span>
    </div>
    <el-progress
      :percentage="percent"
      :stroke-width="6"
      :color="progressColor"
      style="margin-top: 8px"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['done'])

const percent = ref(0)
const elapsed = ref(0)
let timer = null
let percentTimer = null
let startTime = 0

const progressColor = () => {
  if (percent.value < 30) return '#67c23a'
  if (percent.value < 60) return '#409eff'
  if (percent.value < 85) return '#e6a23c'
  return '#f56c6c'
}

const updatePercent = () => {
  const now = Date.now()
  const seconds = (now - startTime) / 1000

  if (seconds <= 5) {
    // 0-5秒：快速增长，从0到60
    percent.value = Math.min(60, Math.round((seconds / 5) * 60))
  } else if (seconds <= 15) {
    // 5-15秒：缓慢增长，从60到85
    percent.value = Math.min(85, 60 + Math.round(((seconds - 5) / 10) * 25))
  } else if (seconds <= 30) {
    // 15-30秒：极慢增长，从85到95
    percent.value = Math.min(95, 85 + Math.round(((seconds - 15) / 15) * 10))
  } else {
    // >30秒：几乎停止，极限98
    percent.value = Math.min(98, 95 + Math.round(Math.min((seconds - 30) / 60, 1) * 3))
  }
}

const startTimers = () => {
  startTime = Date.now()
  // 秒数更新
  timer = setInterval(() => {
    elapsed.value = Math.round((Date.now() - startTime) / 1000)
  }, 200)
  // 进度更新（每200ms）
  percentTimer = setInterval(updatePercent, 200)
}

const finish = () => {
  percent.value = 100
  elapsed.value = Math.round((Date.now() - startTime) / 1000)
  clearInterval(timer)
  clearInterval(percentTimer)
  timer = null
  percentTimer = null
  setTimeout(() => {
    emit('done')
  }, 400)
}

defineExpose({ finish })

onMounted(() => {
  startTimers()
})

onUnmounted(() => {
  clearInterval(timer)
  clearInterval(percentTimer)
})
</script>

<style scoped>
.thinking-progress {
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #d9ecff;
}
.thinking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #409eff;
}
.elapsed-time {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
  font-variant-numeric: tabular-nums;
}
</style>
