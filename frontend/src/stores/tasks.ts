import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '../api/http'

// 重新定义API函数以避免类型导入问题
interface CreateTaskPayload {
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

function createTaskRequest(payload: CreateTaskPayload) {
  return http.post('/tasks', payload).then((res) => res.data.data)
}

function fetchTasks(params?: Record<string, string | number | undefined>) {
  return http
    .get('/tasks', { params })
    .then((res) => res.data.data)
}

function fetchTaskById(id: number) {
  return http.get(`/tasks/${id}`).then((res) => res.data.data)
}

function acceptTaskRequest(id: number) {
  return http.post(`/tasks/${id}/accept`).then((res) => res.data.data)
}

function updateTaskStatusRequest(id: number, status: string) {
  return http
    .post(`/tasks/${id}/status`, { status })
    .then((res) => res.data.data)
}

function cancelTaskRequest(id: number) {
  return http
    .post(`/tasks/${id}/cancel`)
    .then((res) => res.data.data)
}

export interface Task {
  id: number
  title: string
  description: string
  rewardAmount: number
  pickupLocationName: string
  dropoffLocationName: string
  status: string
  cancelledBy?: string
  // 新增字段
  category?: string
  urgency?: string
  pickupLat?: number
  pickupLng?: number
  dropoffLat?: number
  dropoffLng?: number
  createdAt: string
  createdBy?: {
    id: number
    fullName: string
    creditScore: number
  }
  assignedTo?: {
    id: number
    fullName: string
  }
}

export const TASK_STATUS_LABELS: Record<string, string> = {
  pending: '待接单',
  accepted: '已接单',
  picked: '已取件',
  delivering: '派送中',
  confirming: '待确认',
  completed: '已完成',
  cancelled: '已取消',
}

export const TASK_CATEGORY_LABELS: Record<string, string> = {
  delivery: '快递代取',
  food: '餐饮代买',
  document: '文件传递',
  purchase: '物品代购',
  other: '其他'
}

export const TASK_URGENCY_LABELS: Record<string, string> = {
  low: '一般',
  medium: '较急',
  high: '紧急'
}

export const useTaskStore = defineStore('tasks', () => {
  const items = ref<Task[]>([])
  const loading = ref(false)
  const currentTask = ref<Task | null>(null)

  async function loadTasks(params?: Record<string, string | number>) {
    loading.value = true
    try {
      items.value = await fetchTasks(params)
    } finally {
      loading.value = false
    }
  }

  async function loadTask(id: number) {
    currentTask.value = await fetchTaskById(id)
  }

  async function createTask(payload: CreateTaskPayload) {
    const task = await createTaskRequest(payload)
    items.value.unshift(task)
    return task
  }

  async function acceptTask(id: number) {
    const task = await acceptTaskRequest(id)
    await loadTasks()
    currentTask.value = task
  }

  async function updateTaskStatus(id: number, status: string) {
    const task = await updateTaskStatusRequest(id, status)
    await loadTasks()
    currentTask.value = task
  }

  async function cancelTask(id: number) {
    const task = await cancelTaskRequest(id)
    await loadTasks()
    currentTask.value = task
  }

  return {
    items,
    loading,
    currentTask,
    loadTasks,
    loadTask,
    createTask,
    acceptTask,
    updateTaskStatus,
    cancelTask,
  }
})