import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '../api/api-service'

// 从API服务导入类型
// 从API服务导入类型
import type { CreateTaskPayload, Task } from '../api/tasks'


// 任务状态标签
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
      const response = await apiService.tasks.list(params);
      if (response.success) {
        items.value = response.data;
      } else {
        console.error('获取任务列表失败:', response.message);
      }
    } finally {
      loading.value = false
    }
  }

  async function loadTask(id: number) {
    const response = await apiService.tasks.get(id);
    if (response.success) {
      currentTask.value = response.data;
    } else {
      console.error('获取任务详情失败:', response.message);
    }
  }

  async function createTask(payload: CreateTaskPayload) {
    const response = await apiService.tasks.create(payload);
    if (response.success) {
      const task = response.data;
      items.value.unshift(task);
      return task;
    } else {
      console.error('创建任务失败:', response.message);
      throw new Error(response.message);
    }
  }

  async function acceptTask(id: number) {
    const response = await apiService.tasks.accept(id);
    if (response.success) {
      const task = response.data;
      await loadTasks();
      currentTask.value = task;
      return task;
    } else {
      console.error('接取任务失败:', response.message);
      throw new Error(response.message);
    }
  }

  async function updateTaskStatus(id: number, status: string) {
    const response = await apiService.tasks.updateStatus(id, status);
    if (response.success) {
      const task = response.data;
      await loadTasks();
      currentTask.value = task;
      return task;
    } else {
      console.error('更新任务状态失败:', response.message);
      throw new Error(response.message);
    }
  }

  async function cancelTask(id: number) {
    const response = await apiService.tasks.cancel(id);
    if (response.success) {
      const task = response.data;
      await loadTasks();
      currentTask.value = task;
      return task;
    } else {
      console.error('取消任务失败:', response.message);
      throw new Error(response.message);
    }
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