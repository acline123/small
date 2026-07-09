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
          @refresh="fetchSessions"
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
            <div class="input-box">
              <div v-if="attachedFile" class="attachment-bar">
                <el-tag closable type="info" @close="clearAttachment">
                  {{ attachedFile.name }}
                </el-tag>
              </div>
              <el-input
                v-model="input"
                type="textarea"
                :rows="2"
                placeholder="输入问题，Enter 发送，Shift+Enter 换行"
                @keydown="handleKeydown"
              />
            </div>
            <input
              ref="fileInputRef"
              type="file"
              class="hidden-file-input"
              accept=".pdf,.docx,.txt,.pptx"
              @change="handleFileSelect"
            />
            <el-button :disabled="loading" @click="triggerFileSelect">附件</el-button>
            <el-button type="primary" :loading="loading" @click="send">发送</el-button>
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
import { uploadDocument } from '../api/document'

const sessionId = ref(localStorage.getItem('session_id') || '')
const messages = ref([])
const sessions = ref([])
const input = ref('')
const attachedFile = ref(null)
const fileInputRef = ref(null)
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
  attachedFile.value = null
}

const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const ext = file.name.includes('.') ? file.name.split('.').pop().toLowerCase() : ''
  if (!['pdf', 'docx', 'txt', 'pptx'].includes(ext)) {
    ElMessage.warning('仅支持 PDF、DOCX、TXT、PPTX 格式')
    return
  }

  attachedFile.value = file
}

const clearAttachment = () => {
  attachedFile.value = null
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    send()
  }
}

const sendMessage = async (text) => {
  if (!text) return

  messages.value.push({ role: 'user', content: text })

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
}

const send = async () => {
  const text = input.value.trim()
  const file = attachedFile.value
  if ((!text && !file) || loading.value) return

  loading.value = true
  const pendingText = text
  const pendingFile = file
  let uploadDone = false

  try {
    if (pendingFile) {
      await uploadDocument(pendingFile)
      attachedFile.value = null
      uploadDone = true
      if (!pendingText) {
        ElMessage.success('附件已上传至知识库')
        return
      }
    }

    input.value = ''
    await sendMessage(pendingText)
  } catch {
    input.value = pendingText
    if (!uploadDone) {
      attachedFile.value = pendingFile
    }
    const last = messages.value[messages.value.length - 1]
    if (last?.role === 'user' && last.content === pendingText) {
      messages.value.pop()
    }
    ElMessage.error('发送失败，请检查后端是否运行及 API Key 是否配置')
  } finally {
    loading.value = false
  }
}

const quickSend = async (text) => {
  if (loading.value) return
  loading.value = true
  try {
    await sendMessage(text)
  } catch {
    messages.value.pop()
    ElMessage.error('发送失败，请检查后端是否运行及 API Key 是否配置')
  } finally {
    loading.value = false
  }
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
.input-box {
  flex: 1;
}
.input-box .el-textarea {
  width: 100%;
}
.attachment-bar {
  margin-bottom: 8px;
}
.hidden-file-input {
  display: none;
}
</style>







