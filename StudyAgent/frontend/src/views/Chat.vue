<template>
  <div class="chat-page">
    <h2>智能问答</h2>
    <el-card shadow="never" class="chat-card">
      <div class="chat-layout">
        <ChatHistory
          :sessions="sessions"
          :active-id="sessionId"
          @select="loadSession"
          @new-chat="newChat"
        />
        <div class="chat-main">
          <ChatWindow
            :messages="messages"
            :loading="loading"
            @quick-send="quickSend"
          />
          <div class="input-area">
            <el-switch
              v-model="webSearch"
              active-text="联网搜索"
              inactive-text="知识库"
              style="margin-right: 12px"
            />
            <el-input
              v-model="input"
              type="textarea"
              :rows="2"
              placeholder="输入问题，例如：TCP是什么？"
              @keydown.enter.ctrl="send"
            />
            <el-button type="primary" :loading="loading" @click="send">发送 (Ctrl+Enter)</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ChatHistory from '../components/ChatHistory.vue'
import ChatWindow from '../components/ChatWindow.vue'
import { sendChat, getHistory, getSessions } from '../api/chat'

const sessionId = ref(localStorage.getItem('session_id') || '')
const messages = ref([])
const sessions = ref([])
const input = ref('')
const loading = ref(false)
const webSearch = ref(false)

const fetchSessions = async () => {
  const res = await getSessions()
  sessions.value = res.data || []
}

const loadSession = async (id) => {
  sessionId.value = id
  localStorage.setItem('session_id', id)
  const res = await getHistory(id)
  messages.value = res.data?.messages || []
}

const newChat = () => {
  sessionId.value = ''
  localStorage.removeItem('session_id')
  messages.value = []
}

const sendMessage = async (text) => {
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  loading.value = true

  try {
    const res = await sendChat(sessionId.value || undefined, text, webSearch.value)
    const data = res.data
    sessionId.value = data.session_id
    localStorage.setItem('session_id', data.session_id)
    messages.value.push({
      role: 'assistant',
      content: data.reply,
      tool_used: data.tool_used,
      sources: data.sources,
    })
    fetchSessions()
  } catch {
    messages.value.pop()
    ElMessage.error('发送失败，请检查后端是否运行及 API Key 是否配置')
  } finally {
    loading.value = false
  }
}

const send = async () => {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  await sendMessage(text)
}

const quickSend = (text) => {
  sendMessage(text)
}

onMounted(async () => {
  await fetchSessions()
  if (sessionId.value) {
    await loadSession(sessionId.value)
  }
})
</script>

<style scoped>
h2 {
  margin-bottom: 16px;
}
.chat-card {
  min-height: calc(100vh - 120px);
}
.chat-layout {
  display: flex;
  height: calc(100vh - 180px);
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-left: 16px;
}
.input-area {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  align-items: flex-end;
}
.input-area .el-input {
  flex: 1;
}
</style>
