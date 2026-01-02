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
  // 后端返回的字段名（camelCase）
  createdById?: number;
  assignedToId?: number;
  // 后端返回的完整对象
  createdBy?: {
    id: number;
    email: string;
    fullName: string;
    role: string;
    creditScore: number;
    verified: boolean;
  };
  assignedTo?: {
    id: number;
    email: string;
    fullName: string;
    role: string;
    creditScore: number;
    verified: boolean;
  };
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
  console.log('fetchTaskById called with id:', id, 'type:', typeof id)
  if (!id || isNaN(id)) {
    console.error('fetchTaskById: Invalid task id:', id)
    throw new Error(`Invalid task id: ${id}`)
  }

  return http.get(`/tasks/${id}`)
    .then((res) => {
      console.log('fetchTaskById response for id', id, ':', res.data)
      return res.data.data
    })
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
    .then((res) => {
      // 检查是否是调试模式返回的错误
      if (res.data.success === false) {
        throw new Error(res.data.message);
      }
      return res.data.data;
    })
    .catch((error) => {
      console.error('接取任务失败:', error);
      // 如果是业务错误（200 OK 但 success=false），error.response 可能存在
      const message = error.response?.data?.message || error.message || '接取任务失败';
      throw new Error(message);
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