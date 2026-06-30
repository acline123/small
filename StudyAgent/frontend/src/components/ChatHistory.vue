<template>
  <div class="history-panel">
    <div class="panel-header">
      <span>历史会话</span>
      <el-button type="primary" size="small" @click="$emit('new-chat')">新对话</el-button>
    </div>
    <div
      v-for="s in sessions"
      :key="s.session_id"
      :class="['session-item', { active: s.session_id === activeId }]"
      @click="$emit('select', s.session_id)"
    >
      <div class="title">{{ s.title }}</div>
      <div class="time">{{ s.updated_at }}</div>
    </div>
    <el-empty v-if="!sessions.length" description="暂无会话" />
  </div>
</template>

<script setup>
defineProps({
  sessions: { type: Array, default: () => [] },
  activeId: { type: String, default: '' },
})
defineEmits(['select', 'new-chat'])
</script>

<style scoped>
.history-panel {
  width: 240px;
  border-right: 1px solid #e4e7ed;
  padding: 12px;
  overflow-y: auto;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: bold;
}
.session-item {
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 8px;
  border: 1px solid transparent;
}
.session-item:hover {
  background: #f0f2f5;
}
.session-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}
.title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
