<template>
  <div class="appeals-page">
    <n-page-header>
      <template #title>
        申诉管理
      </template>
      <template #subtitle>
        查看和管理申诉工单
      </template>
    </n-page-header>

    <!-- 申诉列表 -->
    <section class="card">
      <div class="toolbar">
        <h3>我的申诉</h3>
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          发起申诉
        </n-button>
      </div>

      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
        <p>加载申诉记录中...</p>
      </div>
      <div v-else-if="appeals.length === 0" class="empty-state">
        <n-empty description="暂无申诉记录">
          <template #extra>
            <p>如果对任务结果有异议，可以发起申诉</p>
            <n-button type="primary" @click="showCreateModal = true">
              发起申诉
            </n-button>
          </template>
        </n-empty>
      </div>
      <div v-else class="appeals-list">
        <div
          v-for="appeal in appeals"
          :key="appeal.id"
          class="appeal-item"
          @click="openAppealDetail(appeal)"
        >
          <div class="appeal-header">
            <div class="appeal-title">
              <h4>{{ appeal.task?.title || `任务 #${appeal.taskId}` }}</h4>
              <n-tag :type="getStatusTagType(appeal.status)">
                {{ getStatusLabel(appeal.status) }}
              </n-tag>
            </div>
            <span class="appeal-time">{{ formatTime(appeal.createdAt) }}</span>
          </div>

          <div class="appeal-content">
            <p class="appeal-reason">
              {{ appeal.reason.length > 100 ? appeal.reason.slice(0, 100) + '...' : appeal.reason }}
            </p>
            <div v-if="appeal.adminReply" class="appeal-reply">
              <strong>管理员回复：</strong>
              {{ appeal.adminReply.length > 100 ? appeal.adminReply.slice(0, 100) + '...' : appeal.adminReply }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 发起申诉模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      title="发起申诉"
      size="large"
    >
      <n-form :model="appealForm" @submit.prevent="createAppeal">
        <n-form-item label="选择任务" required>
          <n-select
            v-model:value="appealForm.taskId"
            :options="availableTasks"
            placeholder="选择要申诉的任务"
            filterable
          />
        </n-form-item>

        <n-form-item label="申诉原因" required>
          <n-input
            v-model:value="appealForm.reason"
            type="textarea"
            placeholder="详细描述您的申诉原因..."
            :maxlength="500"
            show-count
            :autosize="{ minRows: 4, maxRows: 8 }"
          />
        </n-form-item>

        <n-form-item>
          <n-space>
            <n-button
              type="primary"
              :loading="creating"
              :disabled="!appealForm.taskId || !appealForm.reason.trim()"
              @click="createAppeal"
            >
              提交申诉
            </n-button>
            <n-button @click="showCreateModal = false">
              取消
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { useTaskStore } from '../stores/tasks'
import { getAppeals, createAppeal, type Appeal, type CreateAppealPayload } from '../api/appeal'
import { Add } from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const tasks = useTaskStore()

const appeals = ref<Appeal[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)

const appealForm = ref({
  taskId: null as number | null,
  reason: ''
})

// 可申诉的任务（已完成或已取消的任务）
const availableTasks = computed(() => {
  return tasks.items
    .filter(task => ['completed', 'cancelled'].includes(task.status))
    .map(task => ({
      label: task.title,
      value: task.id
    }))
})

// 格式化时间
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    rejected: '已拒绝'
  }
  return labels[status as keyof typeof labels] || status
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const types = {
    pending: 'warning',
    processing: 'info',
    resolved: 'success',
    rejected: 'error'
  }
  return types[status as keyof typeof types] || 'default'
}

// 加载申诉列表
const loadAppeals = async () => {
  loading.value = true
  try {
    const response = await getAppeals()
    if (response.success && response.data) {
      appeals.value = response.data
    }
  } catch (error) {
    console.error('加载申诉列表失败:', error)
    message.error('加载申诉列表失败')
  } finally {
    loading.value = false
  }
}

// 创建申诉
const handleCreateAppeal = async () => {
  if (!appealForm.value.taskId || !appealForm.value.reason.trim()) return

  const payload: CreateAppealPayload = {
    taskId: appealForm.value.taskId,
    reason: appealForm.value.reason.trim()
  }

  creating.value = true
  try {
    const response = await createAppeal(payload)
    if (response.success) {
      message.success('申诉提交成功！')
      showCreateModal.value = false
      appealForm.value = { taskId: null, reason: '' }
      await loadAppeals() // 刷新列表
    } else {
      message.error(response.message || '申诉提交失败')
    }
  } catch (error: any) {
    message.error(error.message || '申诉提交失败')
  } finally {
    creating.value = false
  }
}

// 打开申诉详情
const openAppealDetail = (appeal: Appeal) => {
  // 这里可以跳转到申诉详情页面
  console.log('查看申诉详情:', appeal)
}

// 创建申诉（处理表单提交）
const createAppeal = () => {
  handleCreateAppeal()
}

onMounted(async () => {
  await tasks.loadTasks() // 加载任务列表
  await loadAppeals()
})
</script>

<style scoped>
.appeals-page {
  max-width: 800px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.empty-state {
  padding: 3rem;
}

.appeals-list {
  display: flex;
  flex-direction: column;
}

.appeal-item {
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-medium);
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.appeal-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-light);
}

.appeal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.appeal-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.appeal-title h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.appeal-time {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.appeal-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.appeal-reason {
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
}

.appeal-reply {
  background: var(--bg-tertiary);
  padding: 0.75rem;
  border-radius: var(--radius-small);
  border-left: 3px solid var(--success-color);
  font-size: 0.9rem;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .appeal-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .appeal-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
