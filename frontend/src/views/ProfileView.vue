<template>
  <div class="profile-page" v-if="auth.user">
    <section class="card profile-header">
      <div class="avatar-section">
        <n-avatar :size="72" round>
          {{ initials }}
        </n-avatar>
      </div>
      <div class="user-info">
        <h2>{{ auth.user.fullName }}</h2>
        <p>{{ auth.user.email }}</p>
        <p>校区：{{ auth.user.campus ?? '未填写' }}</p>
        <n-tag type="success" size="small">
          信用分 {{ auth.user.creditScore }}
        </n-tag>
      </div>
      <div class="actions">
        <n-button @click="showEditModal = true">编辑资料</n-button>
        <n-button @click="logout" type="error" ghost>退出登录</n-button>
      </div>
    </section>

    <!-- 新增统计数据图表 -->
    <section class="card stats-chart">
      <h3>我的数据</h3>
      <div class="chart-container">
        <n-grid cols="1 600:3" responsive="screen" :x-gap="20" :y-gap="20">
          <n-grid-item>
            <n-card title="信用评分">
              <div class="chart-placeholder">
                <n-progress type="circle" :percentage="(auth.user.creditScore / 5) * 100"
                  :color="getColorFromScore(auth.user.creditScore)">
                  <span style="font-size: 18px; font-weight: bold;">{{ auth.user.creditScore }}</span>
                </n-progress>
                <p>当前评分 (满分5.0)</p>
                <n-tag v-if="auth.creditInfo?.score_trend" :type="getTrendType(auth.creditInfo.score_trend)"
                  size="small" style="margin-top: 8px;">
                  {{ getTrendLabel(auth.creditInfo.score_trend) }}
                </n-tag>
              </div>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="任务完成率">
              <div class="chart-placeholder">
                <n-statistic label="发布任务完成率"
                  :value="auth.creditInfo?.completion_rates?.publish ? (auth.creditInfo.completion_rates.publish * 100).toFixed(1) + '%' : '暂无数据'"
                  value-style="color: #18a058;" />
                <n-statistic label="接单任务完成率"
                  :value="auth.creditInfo?.completion_rates?.take ? (auth.creditInfo.completion_rates.take * 100).toFixed(1) + '%' : '暂无数据'"
                  value-style="color: #2080f0;" style="margin-top: 20px;" />
              </div>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="等级目标">
              <div class="chart-placeholder">
                <div v-if="auth.creditInfo?.next_level_requirements">
                  <n-statistic :label="`目标: ${auth.creditInfo.next_level_requirements.next_level}`"
                    :value="auth.creditInfo.next_level_requirements.remaining_score + ' 分'"
                    value-style="color: #f0a020;" />
                  <p style="margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
                    {{ auth.creditInfo.next_level_requirements.description }}
                  </p>
                </div>
                <div v-else>
                  <p style="color: #18a058; font-weight: bold;">🎉 已达最高等级！</p>
                </div>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
    </section>

    <!-- 新增我的任务列表 -->
    <section class="card my-tasks">
      <h3>我的任务</h3>
      <n-tabs type="segment" v-model:value="activeTab">
        <n-tab-pane name="created" tab="我发布的">
          <n-empty v-if="createdTasks.length === 0" description="暂无发布的任务">
            <template #extra>
              <router-link to="/tasks/create">
                <n-button>去发布任务</n-button>
              </router-link>
            </template>
          </n-empty>
          <div v-else class="task-list">
            <article v-for="task in createdTasks" :key="task.id" class="task-item">
              <div>
                <h4>{{ task.title }}</h4>
                <div class="task-meta">
                  <n-tag type="info" size="small">{{ categoryLabel(task.category) }}</n-tag>
                  <p class="status">{{ statusLabel(task.status) }}</p>
                </div>
              </div>
              <strong>{{ task.rewardAmount }} 元</strong>
            </article>
          </div>
        </n-tab-pane>
        <n-tab-pane name="accepted" tab="我接单的">
          <n-empty v-if="acceptedTasks.length === 0" description="暂无接单的任务" />
          <div v-else class="task-list">
            <article v-for="task in acceptedTasks" :key="task.id" class="task-item">
              <div>
                <h4>{{ task.title }}</h4>
                <div class="task-meta">
                  <n-tag type="info" size="small">{{ categoryLabel(task.category) }}</n-tag>
                  <p class="status">{{ statusLabel(task.status) }}</p>
                </div>
              </div>
              <strong>{{ task.rewardAmount }} 元</strong>
            </article>
          </div>
        </n-tab-pane>
      </n-tabs>
    </section>

    <!-- 编辑资料模态框 -->
    <n-modal v-model:show="showEditModal" preset="card" style="width: 500px;" title="编辑个人资料">
      <n-form :model="editForm" :rules="editRules" ref="editFormRef">
        <n-form-item label="姓名" path="fullName">
          <n-input v-model:value="editForm.fullName" placeholder="请输入姓名" />
        </n-form-item>
        <n-form-item label="手机号" path="phone">
          <n-input v-model:value="editForm.phone" placeholder="请输入手机号" />
        </n-form-item>
        <n-form-item label="所属校区" path="campus">
          <n-input v-model:value="editForm.campus" placeholder="请输入校区" />
        </n-form-item>
        <div class="form-actions">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="saveProfile" :loading="saving">保存</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useTaskStore, TASK_STATUS_LABELS, TASK_CATEGORY_LABELS } from '../stores/tasks'
import {
  NTag,
  NProgress,
  NGrid,
  NGridItem,
  NCard,
  NTabs,
  NTabPane,
  NStatistic,
  NEmpty,
  NAvatar,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NButton,
  useMessage
} from 'naive-ui'
import { useRouter } from 'vue-router'
import type { FormInst, FormRules } from 'naive-ui'

const auth = useAuthStore()
const tasks = useTaskStore()
const router = useRouter()
const message = useMessage()

const activeTab = ref('created')
const showEditModal = ref(false)
const saving = ref(false)
const editFormRef = ref<FormInst | null>(null)

// 模拟数据
const monthlyTasks = ref(8)
const totalCompleted = ref(24)

// 编辑表单
const editForm = ref({
  fullName: '',
  phone: '',
  campus: ''
})

// 编辑表单验证规则
const editRules: FormRules = {
  fullName: [
    { required: true, message: '请输入姓名' },
    { min: 2, message: '姓名至少2个字符' }
  ],
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1\d{10}$/, message: '请输入合法手机号' }
  ],
  campus: [
    { required: true, message: '请输入校区' },
  ]
}

const initials = computed(() => auth.user?.fullName?.slice(0, 1) ?? '')

// 获取用户创建的任务
const createdTasks = computed(() => {
  return tasks.items.filter(task => task.createdBy?.id === auth.user?.id).slice(0, 5)
})

// 获取用户接单的任务
const acceptedTasks = computed(() => {
  return tasks.items.filter(task => task.assignedTo?.id === auth.user?.id).slice(0, 5)
})

function statusLabel(status: string) {
  return TASK_STATUS_LABELS[status] ?? status
}

// 获取任务分类标签
function categoryLabel(category: string): string {
  return TASK_CATEGORY_LABELS[category] ?? category
}

function getColorFromScore(score: number): string {
  if (score >= 4.0) return '#10b981'  // 优秀
  if (score >= 3.0) return '#f59e0b'  // 良好
  return '#ef4444'  // 需要改进
}

function getTrendType(trend: string): string {
  switch (trend) {
    case 'excellent': return 'success'
    case 'good': return 'info'
    case 'fair': return 'warning'
    case 'poor': return 'error'
    default: return 'default'
  }
}

function getTrendLabel(trend: string): string {
  switch (trend) {
    case 'excellent': return '表现优秀'
    case 'good': return '表现良好'
    case 'fair': return '表现一般'
    case 'poor': return '需要改进'
    default: return '暂无数据'
  }
}

function logout() {
  auth.logout()
  // 退出登录后跳转到登录页面
  router.push('/login')
}

// 保存个人资料
async function saveProfile() {
  editFormRef.value?.validate(async (errors) => {
    if (!errors) {
      saving.value = true
      try {
        // 调用API更新用户信息
        await auth.updateUserProfile({
          fullName: editForm.value.fullName,
          phone: editForm.value.phone,
          campus: editForm.value.campus
        })

        message.success('资料更新成功')
        showEditModal.value = false
      } catch (error) {
        message.error('更新失败: ' + (error as Error).message)
      } finally {
        saving.value = false
      }
    }
  })
}

onMounted(async () => {
  if (!auth.user) {
    await auth.getCurrentUser()
  }
  // 确保信用信息已加载
  if (auth.isAuthenticated && !auth.creditInfo) {
    await auth.loadCreditInfo()
  }
  // 加载任务数据
  await tasks.loadTasks()

  // 初始化编辑表单
  if (auth.user) {
    editForm.value = {
      fullName: auth.user.fullName || '',
      phone: auth.user.phone || '',
      campus: auth.user.campus || ''
    }
  }
})
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  padding: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 0.5rem 0;
}

.user-info p {
  margin: 0.25rem 0;
  color: var(--text-secondary);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 新增样式 */
.stats-chart h3,
.my-tasks h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.chart-container {
  margin-top: 1rem;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.chart-placeholder p {
  margin-top: 1rem;
  color: var(--text-secondary);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-small);
}

.task-item h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>