import axios from "axios"
import request from "./request"

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append("file", file)
  return request.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
}

export function uploadDocumentWithProgress(file, onProgress) {
  const formData = new FormData()
  formData.append("file", file)
  const baseURL = import.meta.env.VITE_API_BASE_URL || "/api"

  return new Promise((resolve, reject) => {
    axios.post(baseURL + "/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total > 0 && onProgress) {
          onProgress(Math.round((progressEvent.loaded / progressEvent.total) * 100))
        }
      },
    }).then((res) => resolve(res.data)).catch((err) => reject(err))
  })
}

export function getDocuments() {
  return request.get("/documents")
}

export function deleteDocument(id) {
  return request.delete("/document", { params: { id } })
}

export function rebuildDocument(id) {
  return request.post("/document/rebuild", { document_id: id })
}

export function getDocumentContent(id) {
  return request.get("/document/content", { params: { id } })
}
