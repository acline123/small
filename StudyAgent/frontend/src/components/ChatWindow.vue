<template>
  <div class="chat-window" ref="windowRef">
    <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-row', msg.role]">
      <div class="bubble">
        <div class="role-label">{{ msg.role === 'user' ? '我' : 'Agent' }}</div>
        <div class="content">{{ msg.content }}</div>
        <div v-if="msg.tool_used" class="tool-tag">
          <el-tag size="small" type="info">工具: {{ msg.tool_used }}</el-tag>
        </div>
      </div>
    </div>
    <div v-if="loading" class="msg-row assistant">
      <div class="bubble"><el-icon class="is-loading"><Loading /></el-icon> 思考中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const windowRef = ref(null)

watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (windowRef.value) {
      windowRef.value.scrollTop = windowRef.value.scrollHeight
    }
  }
)
</script>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}
.msg-row {
  display: flex;
  margin-bottom: 16px;
}
.msg-row.user {
  justify-content: flex-end;
}
.msg-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.user .bubble {
  background: #409eff;
  color: #fff;
}
.role-label {
  font-size: 12px;
  opacity: 0.7;
  margin-bottom: 4px;
}
.content {
  white-space: pre-wrap;
  line-height: 1.6;
}
.tool-tag {
  margin-top: 8px;
}
</style>
