import api from './api'
import type { Document } from '../types'

export async function listDocuments(): Promise<Document[]> {
  const { data } = await api.get<Document[]>('/documents/')
  return data
}

export async function uploadDocument(
  file: File,
  onProgress?: (pct: number) => void,
): Promise<Document> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<Document>('/documents/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded / e.total) * 100))
    },
  })
  return data
}

export async function deleteDocument(id: number): Promise<void> {
  await api.delete(`/documents/${id}`)
}
