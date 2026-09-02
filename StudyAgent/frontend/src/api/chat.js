import request from "./request"

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export function sendChat(sessionId, message, webSearch = false) {
  return request.post("/chat", { session_id: sessionId, message, web_search: webSearch })
}

// 流式对话（SSE）：onDelta 逐段回调；Promise resolve 返回 done 事件的元信息
export function sendChatStream(sessionId, message, webSearch = false, onDelta) {
  return fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message, web_search: webSearch }),
  }).then(async (resp) => {
    if (!resp.ok || !resp.body) {
      let msg = `HTTP ${resp.status}`
      try {
        const err = await resp.json()
        msg = err.message || msg
      } catch { /* 非 JSON 响应体 */ }
      throw new Error(msg)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ""
    let meta = null

    const processEvent = (raw) => {
      for (const line of raw.split("\n")) {
        if (!line.startsWith("data:")) continue
        const payload = JSON.parse(line.slice(5).trim())
        if (payload.type === "delta") {
          onDelta?.(payload.content)
        } else if (payload.type === "done") {
          meta = payload
        } else if (payload.type === "error") {
          throw new Error(payload.message || "流式响应出错")
        }
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buf.indexOf("\n\n")) !== -1) {
        const raw = buf.slice(0, idx)
        buf = buf.slice(idx + 2)
        processEvent(raw)
      }
    }
    if (buf.trim()) processEvent(buf)
    if (!meta) throw new Error("流式响应中断")
    return meta
  })
}

export function getHistory(sessionId) {
  return request.get("/history", { params: { session_id: sessionId } })
}

export function getSessions() {
  return request.get("/history")
}

export function deleteSession(sessionId) {
  return request.delete("/session", { params: { session_id: sessionId } })
}

export function togglePin(sessionId) {
  return request.put("/session/pin", { session_id: sessionId })
}

export function renameSession(sessionId, title) {
  return request.put("/session/rename", { session_id: sessionId, title: title })
}
