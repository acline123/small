import request from './request'

export function sendChat(sessionId, message, webSearch = false) {
  return request.post('/chat', { session_id: sessionId, message, web_search: webSearch })
}

export function getHistory(sessionId) {
  return request.get('/history', { params: { session_id: sessionId } })
}

export function getSessions() {
  return request.get('/history')
}
