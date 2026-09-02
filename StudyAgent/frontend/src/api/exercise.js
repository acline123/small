import request from './request'

// 评估知识水平
export function assessLevel(sessionId) {
  return request.post('/exercise/assess', { session_id: sessionId })
}

// 生成习题
export function generateExercise(sessionId, types, count, documentId) {
  return request.post('/exercise/generate', {
    session_id: sessionId,
    types: types || ['choice', 'true_false', 'fill_blank'],
    count: count || 5,
    document_id: documentId || null,
  })
}

// 提交答案
export function submitAnswer(sessionId, answers) {
  return request.post('/exercise/submit', {
    session_id: sessionId,
    answers: answers,
  })
}

// 答题历史
export function getExerciseHistory(sessionId) {
  return request.get('/exercise/history', { params: { session_id: sessionId } })
}

// 答题统计
export function getExerciseStats(sessionId) {
  return request.get('/exercise/stats', { params: { session_id: sessionId } })
}
