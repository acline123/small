import request from './request'

export function generateSummary(documentId) {
  return request.post('/summary', { document_id: documentId })
}
