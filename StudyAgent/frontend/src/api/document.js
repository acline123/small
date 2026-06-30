import request from './request'

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getDocuments() {
  return request.get('/documents')
}

export function deleteDocument(id) {
  return request.delete('/document', { params: { id } })
}
