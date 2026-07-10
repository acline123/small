<template>
  <div class="chat-window" ref="windowRef">
    <div v-if="!messages.length && !loading" class="welcome">
      <h3>智能学习助手</h3>
      <p>支持知识库问答、联网搜索</p>
      <div class="quick-prompts">
        <el-tag
          v-for="item in quickPrompts"
          :key="item"
          class="prompt-tag"
          effect="plain"
          @click="$emit('quick-send', item)"
        >
          {{ item }}
        </el-tag>
      </div>
    </div>

    <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-row', msg.role]">
      <div class="bubble">
        <div class="role-label">{{ msg.role === 'user' ? '我' : 'Agent' }}</div>
        <div class="content">
          <template v-for="(part, pi) in parseContent(msg.content)" :key="pi">
            <pre v-if="part.type === 'code'" class="code-block"><code>{{ part.text }}</code></pre>
            <div v-else-if="part.type === 'html'" class="text-part" v-html="part.text"></div>
            <span v-else class="text-part">{{ part.text }}</span>
          </template>
        </div>
        <div v-if="msg.tool_used" class="tool-tag">
          <el-tag size="small" type="info">工具: {{ msg.tool_used }}</el-tag>
        </div>
        <div v-if="msg.sources && msg.sources.length" class="sources">
          <div class="sources-title">参考来源：</div>
          <div v-for="(src, i) in msg.sources" :key="i" class="source-item">
            <template v-if="src.url">
              <a :href="src.url" target="_blank" rel="noopener">{{ src.title || src.url }}</a>
            </template>
            <template v-else-if="src.filename">
              {{ src.filename }}
            </template>
            <template v-else-if="src.name">
              {{ src.name }}（{{ src.type }}）
            </template>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showThinking" class="msg-row assistant">
      <div class="bubble">
        <ThinkingProgress ref="thinkingRef" @done="showThinking = false" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import ThinkingProgress from './ThinkingProgress.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['quick-send'])

const windowRef = ref(null)
const thinkingRef = ref(null)
const showThinking = ref(false)

watch(() => props.loading, (val) => {
  if (val) {
    showThinking.value = true
  } else if (showThinking.value && thinkingRef.value) {
    thinkingRef.value.finish()
  }
})

const quickPrompts = [
  'TCP 和 UDP 的区别',
  '什么是 RAG？',
  '帮我搜索知识库中的相关内容',
  '总结一下上传的文档',
]

const parseContent = (text) => {
  if (!text) return [{ type: 'text', text: '' }]
  const parts = []
  const regex = /```(?:\w*\n)?([\s\S]*?)```/g
  let lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'html', text: renderMarkdown(text.slice(lastIndex, match.index)) })
    }
    parts.push({ type: 'code', text: match[1].trim() })
    lastIndex = regex.lastIndex
  }
  if (lastIndex < text.length) {
    parts.push({ type: 'html', text: renderMarkdown(text.slice(lastIndex)) })
  }
  return parts.length ? parts : [{ type: 'text', text }]
}

const renderMarkdown = (text) => {
  // 先转义 HTML，再转换 markdown 语法
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 标题 ### / ## / #
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')

  // 粗体 **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // 斜体 *text*
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // 行内代码 `code`
  html = html.replace(/`(.+?)`/g, '<code class="inline-code">$1</code>')

  // 链接 [text](url)
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')

  // 无序列表项 - item
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')

  // 有序列表项 1. item
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  // 引用 > text
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')

  // 分隔线 ---
  html = html.replace(/^---+$/gm, '<hr>')

  // 换行保留
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  return '<p>' + html + '</p>'
}

watch(
  () => [props.messages.length, props.loading],
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
.welcome {
  text-align: center;
  padding: 40px 20px;
  color: #606266;
}
.welcome h3 {
  margin-bottom: 8px;
  color: #303133;
}
.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}
.prompt-tag {
  cursor: pointer;
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
  line-height: 1.6;
}
.text-part {
  white-space: pre-wrap;
}
.text-part :deep(h2),
.text-part :deep(h3),
.text-part :deep(h4) {
  margin: 8px 0 4px 0;
  font-weight: bold;
}
.text-part :deep(h2) { font-size: 18px; }
.text-part :deep(h3) { font-size: 16px; }
.text-part :deep(h4) { font-size: 14px; }
.text-part :deep(strong) { font-weight: bold; }
.text-part :deep(em) { font-style: italic; }
.text-part :deep(li) { margin-left: 16px; }
.text-part :deep(blockquote) {
  border-left: 3px solid #dcdfe6;
  padding-left: 12px;
  color: #909399;
  margin: 8px 0;
}
.text-part :deep(.inline-code) {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 13px;
}
.text-part :deep(a) {
  color: #409eff;
}
.text-part :deep(hr) {
  border: none;
  border-top: 1px solid #e4e7ed;
  margin: 12px 0;
}
.text-part :deep(p) {
  margin: 4px 0;
}
.code-block {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}
.user .code-block {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
}
.tool-tag {
  margin-top: 8px;
}
.sources {
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.85;
}
.sources-title {
  margin-bottom: 4px;
}
.source-item {
  margin-bottom: 2px;
}
.source-item a {
  color: inherit;
  text-decoration: underline;
}
</style>




