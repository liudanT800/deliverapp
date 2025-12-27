<template>
  <div class="task-list">
    <n-data-table
      :columns="columns"
      :data="tasks"
      :loading="loading"
      :pagination="pagination"
      striped
    />
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTag, NDataTable } from 'naive-ui'
import { TASK_STATUS_LABELS, TASK_CATEGORY_LABELS } from '../stores/tasks'
import type { Task } from '../stores/tasks'

const props = defineProps<{
  tasks: Task[]
}>()

const emit = defineEmits<{
  (e: 'task-updated'): void
}>()

const router = useRouter()
const loading = ref(false)

// 分页配置
const pagination = {
  pageSize: 10
}

// 状态标签类型映射
const statusTypeMap: Record<string, any> = {
  pending: 'warning',
  accepted: 'info',
  picked: 'info',
  delivering: 'info',
  confirming: 'info',
  completed: 'success',
  cancelled: 'error'
}

// 分类标签类型映射
const categoryTypeMap: Record<string, any> = {
  delivery: 'info',
  food: 'success',
  document: 'warning',
  purchase: 'error',
  other: 'default'
}

// 表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '任务标题',
    key: 'title',
    ellipsis: true,
    render(row: Task) {
      return h('span', { style: { cursor: 'pointer', color: '#2080f0' }, onClick: () => openTask(row.id) }, row.title)
    }
  },
  {
    title: '分类',
    key: 'category',
    width: 120,
    render(row: Task) {
      return h(
        NTag,
        { type: categoryTypeMap[row.category] || 'default', size: 'small' },
        { default: () => TASK_CATEGORY_LABELS[row.category] || row.category }
      )
    }
  },
  {
    title: '酬金',
    key: 'rewardAmount',
    width: 100,
    render(row: Task) {
      return `¥${row.rewardAmount}`
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render(row: Task) {
      return h(
        NTag,
        { type: statusTypeMap[row.status] || 'default', size: 'small' },
        { default: () => TASK_STATUS_LABELS[row.status] || row.status }
      )
    }
  },
  {
    title: '发布者',
    key: 'createdBy',
    width: 120,
    render(row: Task) {
      return row.createdBy?.fullName || '-'
    }
  },
  {
    title: '接单人',
    key: 'assignedTo',
    width: 120,
    render(row: Task) {
      return row.assignedTo?.fullName || '-'
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render(row: Task) {
      return [
        h(NButton, {
          size: 'small',
          style: { marginRight: '8px' },
          onClick: () => openTask(row.id)
        }, { default: () => '查看详情' }),
        h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => updateTaskStatus(row)
        }, { default: () => '状态管理' })
      ]
    }
  }
]

// 打开任务详情
function openTask(id: number) {
  router.push(`/tasks/${id}`)
}

// 更新任务状态
function updateTaskStatus(task: Task) {
  router.push(`/tasks/${task.id}/status`)
}
</script>

<style scoped>
.task-list {
  margin-top: 1rem;
}
</style>