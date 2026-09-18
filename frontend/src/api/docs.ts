import { http } from './http'

export interface DocInfo {
  id: string
  filename: string
  chunk_count: number
  status: string
  created_at: string
}

export function listDocs(): Promise<DocInfo[]> {
  return http.get<DocInfo[]>('/docs').then((r) => r.data)
}

export function deleteDoc(id: string): Promise<{ ok: boolean }> {
  return http.delete(`/docs/${id}`).then((r) => r.data)
}

export function uploadDoc(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<{ id: string; filename: string; chunk_count: number }> {
  const form = new FormData()
  form.append('file', file)
  return http
    .post('/docs/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      },
    })
    .then((r) => r.data)
}
