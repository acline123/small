import request from './request'

export function getGraph(documentId) {
  return request.get('/graph', { params: documentId ? { document_id: documentId } : {} })
}
