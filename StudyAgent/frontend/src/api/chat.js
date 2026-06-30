import request from './request'

export function sendChat(sessionId, message) {
  return request.post('/chat', { session_id: sessionId, message })
}

export function getHistory(sessionId) {
  return request.get('/history', { params: { session_id: sessionId } })
}

export function getSessions() {
  return request.get('/history')
}
