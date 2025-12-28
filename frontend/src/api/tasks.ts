import http from './http'

export interface Task {
  id: number;
  title: string;
  description: string;
  pickupLocationName: string;
  dropoffLocationName: string;
  rewardAmount: number;
  pickupLat?: number;
  pickupLng?: number;
  dropoffLat?: number;
  dropoffLng?: number;
  status: string;
  cancelledBy?: string;
  createdAt: string;
  updatedAt?: string;
  expiresAt?: string;
  grabExpiresAt?: string;
  category?: string;
  urgency?: string;
  createdById?: number;
  assignedToId?: number;
}

export function fetchTasks(params?: Record<string, string | number | undefined>): Promise<Task[]> {
  return http
    .get('/tasks', { params })
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('获取任务列表失败:', error);
      throw error;
    });
}

export function fetchTaskById(id: number): Promise<Task> {
  return http.get(`/tasks/${id}`)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('获取任务详情失败:', error);
      throw error;
    });
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

export function createTaskRequest(payload: CreateTaskPayload): Promise<Task> {
  return http.post('/tasks', payload)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('创建任务失败:', error);
      throw error;
    });
}

export function acceptTaskRequest(id: number): Promise<Task> {
  return http.post(`/tasks/${id}/accept`)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('接取任务失败:', error);
      throw error;
    });
}

export function updateTaskStatusRequest(id: number, status: string): Promise<Task> {
  return http
    .post(`/tasks/${id}/status`, { status })
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('更新任务状态失败:', error);
      throw error;
    });
}

export function cancelTaskRequest(id: number): Promise<Task> {
  return http
    .post(`/tasks/${id}/cancel`)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('取消任务失败:', error);
      throw error;
    });
}