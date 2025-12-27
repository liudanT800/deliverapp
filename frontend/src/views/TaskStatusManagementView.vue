<template>
  <div class="status-management-page" v-if="task">
    <n-page-header @back="goBack">
      <template #title>
        任务状态管理
      </template>
      <template #subtitle>
        任务ID: {{ task.id }} - {{ task.title }}
      </template>
    </n-page-header>

    <section class="card status-flow">
      <h3>状态流转图</h3>
      <div class="timeline">
        <div 
          v-for="state in timeline" 
          :key="state.key" 
          class="timeline-item"
          :class="{ active: state.key === task.status, completed: isStateCompleted(state.key) }"
        >
          <div class="dot"></div>
          <div class="content">
            <strong>{{ state.label }}</strong>
            <p>{{ state.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="card status-update">
      <h3>更新任务状态</h3>
      <n-form :model="form" :rules="rules" ref="formRef">
        <n-form-item label="当前状态" path="currentStatus">
          <n-tag :type="statusTypeMap[task.status] || 'default'" size="large">
            {{ statusLabel(task.status) }}
          </n-tag>
        </n-form-item>
        
        <n-form-item label="新状态" path="newStatus">
          <n-select
            v-model:value="form.newStatus"
            :options="availableStatusOptions"
            placeholder="选择新的任务状态"
          />
        </n-form-item>
        
        <n-form-item label="备注说明" path="remark">
          <n-input
            v-model:value="form.remark"
            type="textarea"
            placeholder="请输入状态变更的原因或备注"
          />
        </n-form-item>
        
        <n-button type="primary" @click="updateStatus">更新状态</n-button>
      </n-form>
    </section>

    <section class="card status-history">
      <h3>状态变更历史</h3>
      <n-timeline v-if="statusHistory.length > 0">
        <n-timeline-item
          v-for="(record, index) in statusHistory"
          :key="index"
          :time="formatTime(record.time)"
          :type="record.type"
        >
          <template #header>
            <strong>{{ record.operator }}</strong>
          </template>
          <p>{{ statusLabel(record.status) }}</p>
          <p v-if="record.remark">{{ record.remark }}</p>
        </n-timeline-item>
      </n-timeline>
      <n-empty v-else description="暂无状态变更记录" />
    </section>
  </div>
  <n-spin v-else :show="loading" />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore, TASK_STATUS_LABELS } from '../stores/tasks'
import { 
  NPageHeader, 
  NTag, 
  NSelect, 
  NTimeline, 
  NTimelineItem, 
  NEmpty,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSpin
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const tasks = useTaskStore()
const formRef = ref<FormInst | null>(null)

const taskId = Number(route.params.id)
const loading = ref(false)
const task = computed(() => tasks.currentTask)

const form = ref({
  newStatus: '',
  remark: ''
})

const rules: FormRules = {
  newStatus: [{ required: true, message: '请选择新的任务状态' }]
}

// 状态标签映射
const statusLabel = (status: string) => {
  return TASK_STATUS_LABELS[status] || status
}

// 状态类型映射
const statusTypeMap: Record<string, any> = {
  pending: 'warning',
  accepted: 'info',
  picked: 'info',
  delivering: 'info',
  confirming: 'info',
  completed: 'success',
  cancelled: 'error'
}

// 状态流转时间线
const timeline = [
  { key: 'pending', label: '待接单', desc: '等待顺路同学响应' },
  { key: 'accepted', label: '已接单', desc: '接单者已确认任务' },
  { key: 'picked', label: '已取件', desc: '物品已被取走' },
  { key: 'delivering', label: '派送中', desc: '正在前往送达' },
  { key: 'confirming', label: '待确认', desc: '等待双方确认' },
  { key: 'completed', label: '已完成', desc: '任务完成酬金结算' },
  { key: 'cancelled', label: '已取消', desc: '任务已被取消' }
]

// 判断状态是否已完成
const isStateCompleted = (stateKey: string) => {
  const stateOrder = ['pending', 'accepted', 'picked', 'delivering', 'confirming', 'completed', 'cancelled']
  const currentStateIndex = stateOrder.indexOf(task.value?.status || '')
  const stateIndex = stateOrder.indexOf(stateKey)
  return stateIndex >= 0 && stateIndex < currentStateIndex
}

// 可用的状态选项
const availableStatusOptions = computed(() => {
  // 根据当前状态，提供可选的下一个状态
  const nextStatusMap: Record<string, string[]> = {
    pending: ['accepted', 'cancelled'],
    accepted: ['picked', 'cancelled'],
    picked: ['delivering', 'cancelled'],
    delivering: ['confirming', 'cancelled'],
    confirming: ['completed', 'cancelled'],
    completed: [],
    cancelled: []
  }
  
  const nextStatuses = nextStatusMap[task.value?.status || ''] || []
  return nextStatuses.map(status => ({
    label: statusLabel(status),
    value: status
  }))
})

// 状态变更历史（模拟数据）
const statusHistory = ref([
  {
    time: '2025-05-01T10:00:00Z',
    operator: '系统',
    status: 'pending',
    remark: '任务已发布',
    type: 'info'
  },
  {
    time: '2025-05-01T11:30:00Z',
    operator: '张三',
    status: 'accepted',
    remark: '我正好顺路，可以帮忙',
    type: 'success'
  },
  {
    time: '2025-05-01T12:15:00Z',
    operator: '张三',
    status: 'picked',
    remark: '已取到物品',
    type: 'success'
  }
])

// 格式化时间
const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 更新状态
const updateStatus = () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      try {
        await tasks.updateTaskStatus(taskId, form.value.newStatus)
        // 添加到历史记录
        statusHistory.value.unshift({
          time: new Date().toISOString(),
          operator: '管理员',
          status: form.value.newStatus,
          remark: form.value.remark,
          type: 'success'
        })
        // 重置表单
        form.value.newStatus = ''
        form.value.remark = ''
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    }
  })
}

onMounted(async () => {
  loading.value = true
  try {
    await tasks.loadTask(taskId)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.status-management-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  padding: 1.5rem;
}

.status-flow h3,
.status-update h3,
.status-history h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-left: 0.5rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  position: relative;
  padding-left: 1.5rem;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 1.5rem;
  bottom: -0.5rem;
  width: 2px;
  background: var(--border-color);
}

.timeline-item.active::before {
  background: var(--primary-color);
}

.dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #d1d5db;
  position: absolute;
  left: 0;
  top: 0.25rem;
  z-index: 1;
}

.timeline-item.active .dot {
  background: var(--primary-color);
  box-shadow: 0 0 0 4px var(--primary-light);
}

.timeline-item.completed .dot {
  background: var(--success-color);
}

.content strong {
  display: block;
  margin-bottom: 0.25rem;
}

.content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>