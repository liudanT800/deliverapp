import http from './http'

export function fetchTasks(params?: Record<string, string | number | undefined>) {
  return http
    .get('/tasks', { params })
    .then((res) => res.data.data)
}

export function fetchTaskById(id: number) {
  return http.get(`/tasks/${id}`).then((res) => res.data.data)
}

export interface CreateTaskPayload {
  title: string
  description: string
  pickupLocationName: string
  dropoffLocationName: string
  rewardAmount: number
  expiresAt?: string
  grabExpiresAt?: string
  category?: string
  urgency?: string
  pickupLat?: number
  pickupLng?: number
  dropoffLat?: number
  dropoffLng?: number
}

export function createTaskRequest(payload: CreateTaskPayload) {
  return http.post('/tasks', payload).then((res) => res.data.data)
}

export function acceptTaskRequest(id: number) {
  return http.post(`/tasks/${id}/accept`).then((res) => res.data.data)
}

export function updateTaskStatusRequest(id: number, status: string) {
  return http
    .post(`/tasks/${id}/status`, { status })
    .then((res) => res.data.data)
}

export function cancelTaskRequest(id: number) {
  return http
    .post(`/tasks/${id}/cancel`)
    .then((res) => res.data.data)
}