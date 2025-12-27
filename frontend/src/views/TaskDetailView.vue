<template>
  <div v-if="task" class="detail-page">
    <section class="card highlight">
      <header>
        <div>
          <p class="status">{{ statusLabel(task.status) }}</p>
          <h2>{{ task.title }}</h2>
        </div>
        <strong class="reward">{{ task.rewardAmount }} 元</strong>
      </header>
      <p class="desc">{{ task.description }}</p>
      <div class="locations">
        <div>
          <small>取件</small>
          <strong>{{ task.pickupLocationName }}</strong>
        </div>
        <div>
          <small>送达</small>
          <strong>{{ task.dropoffLocationName }}</strong>
        </div>
      </div>
      <!-- 新增任务分类和紧急程度信息 -->
      <div class="task-tags">
        <n-tag type="info">{{ categoryLabel(task.category) }}</n-tag>
        <n-tag :type="urgencyTagType(task.urgency)">{{ urgencyLabel(task.urgency) }}</n-tag>
      </div>
      <!-- 新增任务发布者信息 -->
      <div class="creator-info" v-if="task.createdBy">
        <n-avatar round :size="32">{{ task.createdBy.fullName.slice(0, 1) }}</n-avatar>
        <div>
          <p>任务发布者</p>
          <strong>{{ task.createdBy.fullName }}</strong>
        </div>
        <n-tag type="success" size="small">信用分 {{ task.createdBy.creditScore }}</n-tag>
      </div>
    </section>

    <section class="card">
      <h3>任务流转</h3>
      <div class="timeline">
        <div v-for="state in timeline" :key="state.key" class="timeline-item">
          <span :class="['dot', { active: state.key === task.status }]"></span>
          <div>
            <strong>{{ state.label }}</strong>
            <p>{{ state.desc }}</p>
          </div>
        </div>
      </div>
      <!-- 新增接单人信息 -->
      <div class="assignee-info" v-if="task.assignedTo && task.status !== 'pending'">
        <h4>接单人信息</h4>
        <div class="user-card">
          <n-avatar round :size="48">{{ task.assignedTo.fullName.slice(0, 1) }}</n-avatar>
          <div>
            <strong>{{ task.assignedTo.fullName }}</strong>
            <p>已接单 · 任务进行中</p>
          </div>
        </div>
      </div>
      <div class="actions">
        <n-button text @click="goBack">返回</n-button>
        <n-space>
          <n-button
            v-if="task.status === 'pending' && canAcceptTask"
            type="primary"
            @click="accept"
          >
            接单
          </n-button>
          <n-dropdown
            trigger="click"
            :options="statusOptions"
            @select="updateStatus"
          >
            <n-button secondary>更新状态</n-button>
          </n-dropdown>
          <n-button
            v-if="canCancelTask"
            type="error"
            secondary
            @click="cancelTask"
          >
            取消任务
          </n-button>
        </n-space>
      </div>
    </section>
  </div>
  <n-spin v-else show></n-spin>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { DropdownOption } from 'naive-ui'
import { useTaskStore, TASK_STATUS_LABELS, TASK_CATEGORY_LABELS, TASK_URGENCY_LABELS } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'
import { NAvatar, NTag, useMessage, useNotification } from 'naive-ui'

const tasks = useTaskStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const message = useMessage()
const notification = useNotification()
const taskId = Number(route.params.id)

const task = computed(() => tasks.currentTask)

// 判断当前用户是否可以取消任务
const canCancelTask = computed(() => {
  if (!task.value || !auth.user) return false

  // 任务已完成或已取消则不能取消
  if (['completed', 'cancelled'].includes(task.value.status)) return false

  // 发布者或接单者可以取消任务
  return auth.user.id === task.value.createdBy?.id ||
         (task.value.assignedTo && auth.user.id === task.value.assignedTo.id)
})

// 判断当前用户是否可以接取任务
const canAcceptTask = computed(() => {
  if (!task.value || !auth.user) return false

  // 不能接取自己的任务
  if (auth.user.id === task.value.createdBy?.id) return false

  // 只有pending状态的任务才能被接取
  return task.value.status === 'pending'
})

const timeline = [
  { key: 'pending', label: '待接单', desc: '等待顺路同学响应' },
  { key: 'accepted', label: '已接单', desc: '接单者已确认任务' },
  { key: 'picked', label: '已取件', desc: '物品已被取走' },
  { key: 'delivering', label: '派送中', desc: '正在前往送达' },
  { key: 'confirming', label: '待确认', desc: '等待双方确认' },
  { key: 'completed', label: '已完成', desc: '任务完成酬金结算' },
]

const statusOptions: DropdownOption[] = timeline.map((item) => ({
  label: item.label,
  key: item.key,
}))

function statusLabel(status: string) {
  return TASK_STATUS_LABELS[status] ?? status
}

// 获取任务分类标签
function categoryLabel(category: string): string {
  return TASK_CATEGORY_LABELS[category] ?? category
}

// 获取紧急程度标签
function urgencyLabel(urgency: string): string {
  return TASK_URGENCY_LABELS[urgency] ?? urgency
}

// 根据紧急程度获取标签类型
function urgencyTagType(urgency: string): "default" | "success" | "warning" | "error" {
  switch (urgency) {
    case 'high': return 'error'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'default'
  }
}

async function accept() {
  try {
    await tasks.acceptTask(taskId)
    message.success('任务接取成功')
  } catch (error: any) {
    // 使用通知显示错误信息，而不是抛出异常
    notification.error({
      title: '接取任务失败',
      content: error.response?.data?.message || error.message || '未知错误',
      duration: 5000
    })
  }
}

async function updateStatus(status: string | number | DropdownOption) {
  if (typeof status !== 'string') return
  await tasks.updateTaskStatus(taskId, status)
}

async function cancelTask() {
  try {
    await tasks.cancelTask(taskId)
    message.success('任务已成功取消')
  } catch (error) {
    message.error('取消任务失败: ' + (error as Error).message)
  }
}

function goBack() {
  router.back()
}

onMounted(async () => {
  await tasks.loadTask(taskId)
})
</script>

<style scoped>
.detail-page {
  display: grid;
  gap: 1.5rem;
}

.card {
  padding: 1.75rem;
}

.highlight header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reward {
  font-size: 2rem;
  color: var(--secondary-color);
}

.locations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

/* 新增任务标签样式 */
.task-tags {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

/* 新增样式 */
.creator-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border-color);
}

.creator-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.assignee-info {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border-color);
}

.assignee-info h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-tertiary);
  padding: 1rem;
  border-radius: var(--radius-small);
}

.timeline {
  display: grid;
  gap: 1rem;
  margin: 1.5rem 0;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 0.35rem;
  background: #d1d5db;
}

.dot.active {
  background: var(--primary-color);
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}
</style>