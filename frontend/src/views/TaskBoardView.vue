<template>
  <div class="layout">
    <aside class="filters card">
      <h3>智能筛选</h3>
      <n-form :model="filters" label-placement="top">
        <n-form-item label="关键字">
          <n-input v-model:value="filters.keyword" placeholder="课本 / 钥匙" />
        </n-form-item>
        <n-form-item label="酬金范围">
          <n-slider
            range
            :step="1"
            :max="30"
            v-model:value="filters.reward"
          />
        </n-form-item>
        <n-form-item label="任务状态">
          <n-select
            v-model:value="filters.status"
            :options="statusOptions"
            clearable
          />
        </n-form-item>
        <!-- 新增更多筛选条件 -->
        <n-form-item label="取件地点">
          <n-input v-model:value="filters.pickupLocation" placeholder="宿舍 / 教学楼" />
        </n-form-item>
        <n-form-item label="送达地点">
          <n-input v-model:value="filters.dropoffLocation" placeholder="食堂 / 图书馆" />
        </n-form-item>
        <n-form-item label="发布时间">
          <n-radio-group v-model:value="filters.timeRange" name="timeRange">
            <n-space>
              <n-radio value="all">全部</n-radio>
              <n-radio value="today">今天</n-radio>
              <n-radio value="week">本周</n-radio>
              <n-radio value="month">本月</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>
        <!-- 新增分类筛选 -->
        <n-form-item label="任务分类">
          <n-select
            v-model:value="filters.category"
            :options="categoryOptions"
            clearable
            placeholder="选择任务类型"
          />
        </n-form-item>
        <!-- 新增紧急程度筛选 -->
        <n-form-item label="紧急程度">
          <n-select
            v-model:value="filters.urgency"
            :options="urgencyOptions"
            clearable
            placeholder="选择紧急程度"
          />
        </n-form-item>
        <!-- 新增排序选项 -->
        <n-form-item label="排序方式">
          <n-select
            v-model:value="filters.sortBy"
            :options="sortOptions"
            placeholder="选择排序方式"
          />
        </n-form-item>
        <n-form-item label="排序顺序">
          <n-radio-group v-model:value="filters.sortOrder" name="sortOrder">
            <n-space>
              <n-radio value="asc">升序</n-radio>
              <n-radio value="desc">降序</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>
        <n-button type="primary" block @click="applyFilters">开始匹配</n-button>
        <n-button block @click="resetFilters" style="margin-top: 10px;">重置筛选</n-button>
      </n-form>
    </aside>

    <section class="content">
      <header class="content-header card">
        <div>
          <h2>顺路任务大厅</h2>
          <p>匹配最近 1 公里内的急需互助</p>
        </div>
        <router-link to="/tasks/create">
          <n-button type="primary">发布任务</n-button>
        </router-link>
      </header>

      <n-spin :show="tasks.loading">
        <!-- 新增任务统计信息 -->
        <div class="stats-bar card">
          <n-statistic label="总计任务" :value="tasks.items.length" />
          <n-statistic label="待接单" :value="pendingTasksCount" />
          <n-statistic label="高酬金" :value="highRewardTasksCount" />
        </div>
        
        <div class="task-list">
          <article 
            v-for="task in tasks.items" 
            :key="task.id" 
            class="task-card card"
            @click="openTask(task.id)"
          >
            <div class="task-head">
              <span class="tag">{{ statusLabel(task.status) }}</span>
              <strong class="reward">{{ task.rewardAmount }} 元</strong>
            </div>
            <h3>{{ task.title }}</h3>
            <p class="desc">{{ task.description }}</p>
            <ul class="location">
              <li>
                <small>取件</small>
                <strong>{{ task.pickupLocationName }}</strong>
              </li>
              <li>
                <small>送达</small>
                <strong>{{ task.dropoffLocationName }}</strong>
              </li>
            </ul>
            <!-- 新增任务分类和紧急程度信息 -->
            <div class="task-tags">
              <n-tag type="info" size="small">{{ categoryLabel(task.category) }}</n-tag>
              <n-tag :type="urgencyTagType(task.urgency)" size="small">{{ urgencyLabel(task.urgency) }}</n-tag>
            </div>
            <!-- 新增任务时间信息 -->
            <div class="task-meta">
              <n-tag v-if="isHighReward(task.rewardAmount)" type="warning" size="small">高酬金</n-tag>
              <span class="time">{{ formatTime(task.createdAt) }}</span>
            </div>
            <footer>
              <n-button 
                text 
                @click.stop="openTask(task.id)"
              >
                查看详情
              </n-button>
              <n-button
                v-if="task.status === 'pending'"
                type="primary"
                @click.stop="accept(task.id)"
              >
                顺路接单
              </n-button>
            </footer>
          </article>
        </div>
        
        <!-- 当没有任务时显示 -->
        <n-empty v-if="!tasks.loading && tasks.items.length === 0" description="暂无匹配的任务">
          <template #extra>
            <div class="empty-state-actions">
              <n-button @click="resetFilters">重置筛选条件</n-button>
              <n-button type="primary" @click="router.push('/tasks/create')">发布新任务</n-button>
            </div>
            <div class="empty-state-tips">
              <h4>小贴士：</h4>
              <ul>
                <li>调整筛选条件可能会发现更多任务</li>
                <li>发布任务可以获得帮助</li>
                <li>定期查看任务大厅会有新机会</li>
              </ul>
            </div>
          </template>
        </n-empty>
      </n-spin>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { SelectOption } from 'naive-ui'
import { useTaskStore, TASK_STATUS_LABELS, TASK_CATEGORY_LABELS, TASK_URGENCY_LABELS } from '../stores/tasks'
import { NStatistic, NTag, NEmpty, NRadioGroup, NRadio, NSelect } from 'naive-ui'

const tasks = useTaskStore()
const router = useRouter()

const filters = reactive<{
  keyword: string
  reward: [number, number]
  status: string | null
  pickupLocation: string
  dropoffLocation: string
  timeRange: string
  category: string | null
  urgency: string | null
  sortBy: string
  sortOrder: string
}>({
  keyword: '',
  reward: [0, 30],
  status: null as string | null,
  pickupLocation: '',
  dropoffLocation: '',
  timeRange: 'all',
  category: null as string | null,
  urgency: null as string | null,
  sortBy: 'created_at',
  sortOrder: 'desc'
})

const statusOptions: SelectOption[] = Object.entries(TASK_STATUS_LABELS).map(
  ([value, label]) => ({
    label,
    value,
  }),
)

// 任务分类选项
const categoryOptions: SelectOption[] = Object.entries(TASK_CATEGORY_LABELS).map(
  ([value, label]) => ({
    label,
    value,
  }),
)

// 紧急程度选项
const urgencyOptions: SelectOption[] = Object.entries(TASK_URGENCY_LABELS).map(
  ([value, label]) => ({
    label,
    value,
  }),
)

// 排序选项
const sortOptions: SelectOption[] = [
  { label: '创建时间', value: 'created_at' },
  { label: '酬金金额', value: 'reward_amount' }
]

// 计算待接单任务数量
const pendingTasksCount = computed(() => {
  return tasks.items.filter(task => task.status === 'pending').length
})

// 计算高酬金任务数量（大于等于10元）
const highRewardTasksCount = computed(() => {
  return tasks.items.filter(task => task.rewardAmount >= 10).length
})

// 判断是否为高酬金任务
function isHighReward(amount: number): boolean {
  return amount >= 10
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

// 格式化时间显示
function formatTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return '今天'
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

function applyFilters() {
  tasks.loadTasks({
    keyword: filters.keyword,
    min_reward: filters.reward[0],
    max_reward: filters.reward[1],
    status: filters.status ?? undefined,
    pickup_location: filters.pickupLocation || undefined,
    dropoff_location: filters.dropoffLocation || undefined,
    time_range: filters.timeRange !== 'all' ? filters.timeRange : undefined,
    category: filters.category ?? undefined,
    urgency: filters.urgency ?? undefined,
    sort_by: filters.sortBy,
    sort_order: filters.sortOrder,
  })
}

function resetFilters() {
  filters.keyword = ''
  filters.reward = [0, 30]
  filters.status = null
  filters.pickupLocation = ''
  filters.dropoffLocation = ''
  filters.timeRange = 'all'
  filters.category = null
  filters.urgency = null
  filters.sortBy = 'created_at'
  filters.sortOrder = 'desc'
  tasks.loadTasks()
}

function statusLabel(status: string) {
  return TASK_STATUS_LABELS[status] ?? status
}

function openTask(id: number) {
  router.push(`/tasks/${id}`)
}

async function accept(id: number) {
  await tasks.acceptTask(id)
}

onMounted(async () => {
  await tasks.loadTasks()
})
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.filters {
  padding: 1.5rem;
  animation: slideInLeft 0.3s ease-out;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  padding: 1.5rem;
  align-items: center;
  animation: slideInRight 0.3s ease-out;
}

/* 新增样式 */
.stats-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  animation: slideInRight 0.3s ease-out;
}

.task-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  animation: slideInRight 0.3s ease-out;
}

.task-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  animation: fadeIn 0.3s ease-out;
}

.task-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-heavy);
}

.task-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reward {
  font-size: 1.25rem;
  color: var(--secondary-color);
}

.tag {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
}

.location {
  display: grid;
  gap: 0.5rem;
  padding: 0;
  list-style: none;
}

.location li {
  background: var(--bg-tertiary);
  border-radius: var(--radius-small);
  padding: 0.5rem 0.75rem;
}

/* 新增任务标签样式 */
.task-tags {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* 新增任务元信息样式 */
.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.time {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

footer {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
}

/* 空状态页面样式 */
.empty-state-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: center;
}

.empty-state-tips {
  text-align: left;
  background: var(--bg-tertiary);
  padding: 1rem;
  border-radius: var(--radius-small);
  max-width: 400px;
  margin: 0 auto;
}

.empty-state-tips h4 {
  margin-top: 0;
  color: var(--primary-color);
}

.empty-state-tips ul {
  padding-left: 1.2rem;
  margin-bottom: 0;
  color: var(--text-secondary);
}

/* 新增动画 */
@keyframes slideInLeft {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
