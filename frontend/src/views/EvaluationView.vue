<template>
  <div class="evaluation-page">
    <n-page-header>
      <template #title>
        评价任务
      </template>
      <template #subtitle>
        对任务完成情况进行评价打分
      </template>
      <template #extra>
        <n-button @click="router.back()" quaternary>
          返回
        </n-button>
      </template>
    </n-page-header>

    <!-- 任务信息 -->
    <section class="card task-info">
      <div class="task-header">
        <div>
          <h3>{{ task?.title }}</h3>
          <p>{{ task?.description }}</p>
        </div>
        <div class="task-meta">
          <n-tag type="info">{{ categoryLabel(task?.category) }}</n-tag>
          <n-tag type="success">{{ task?.rewardAmount }} 元</n-tag>
        </div>
      </div>
    </section>

    <!-- 评价表单 -->
    <section class="card evaluation-form">
      <h3>评价对方</h3>
      <p class="evaluation-target">
        评价对象: <strong>{{ evaluateeName }}</strong>
      </p>

      <n-form :model="evaluationForm" @submit.prevent="submitEvaluation">
        <!-- 评分 -->
        <n-form-item label="评分" required>
          <n-rate
            v-model:value="evaluationForm.score"
            :count="5"
            size="large"
            :allow-half="false"
          />
          <div class="score-label">
            {{ getScoreLabel(evaluationForm.score) }}
          </div>
        </n-form-item>

        <!-- 评价内容 -->
        <n-form-item label="评价内容">
          <n-input
            v-model:value="evaluationForm.comment"
            type="textarea"
            placeholder="分享您的使用体验，帮助其他用户做出更好选择..."
            :maxlength="200"
            show-count
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>

        <!-- 提交按钮 -->
        <n-form-item>
          <n-space>
            <n-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="!evaluationForm.score"
              @click="submitEvaluation"
            >
              提交评价
            </n-button>
            <n-button size="large" @click="router.back()">
              暂不评价
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTaskStore, TASK_CATEGORY_LABELS } from '../stores/tasks'
import { submitEvaluation, type SubmitEvaluationPayload } from '../api/evaluation'
import { useMessage } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tasks = useTaskStore()
const message = useMessage()

const taskId = ref(Number(route.params.id))
const task = computed(() => tasks.items.find(t => t.id === taskId.value))
const submitting = ref(false)

const evaluationForm = ref({
  score: 0,
  comment: ''
})

// 评价对象名称
const evaluateeName = computed(() => {
  if (!task.value) return ''
  // 如果当前用户是任务创建者，评价接单者；反之评价创建者
  const isCreator = task.value.createdById === auth.user?.id
  return isCreator
    ? task.value.assignedTo?.fullName || '接单者'
    : task.value.createdBy?.fullName || '发布者'
})

// 任务分类标签
const categoryLabel = (category: string) => {
  return TASK_CATEGORY_LABELS[category] || category
}

// 获取评分标签
const getScoreLabel = (score: number) => {
  const labels = {
    1: '非常不满意',
    2: '不满意',
    3: '一般',
    4: '满意',
    5: '非常满意'
  }
  return labels[score as keyof typeof labels] || ''
}

// 提交评价
const handleSubmitEvaluation = async () => {
  if (!task.value || !evaluationForm.value.score) return

  // 确定被评价者
  const evaluateeId = task.value.createdById === auth.user?.id
    ? task.value.assignedToId
    : task.value.createdById

  if (!evaluateeId) {
    message.error('无法确定评价对象')
    return
  }

  const payload: SubmitEvaluationPayload = {
    taskId: taskId.value,
    evaluateeId: evaluateeId,
    score: evaluationForm.value.score,
    comment: evaluationForm.value.comment || undefined
  }

  submitting.value = true
  try {
    const response = await submitEvaluation(payload)
    if (response.success) {
      message.success('评价提交成功！')
      router.back()
    } else {
      message.error(response.message || '评价提交失败')
    }
  } catch (error: any) {
    message.error(error.message || '评价提交失败')
  } finally {
    submitting.value = false
  }
}

// 提交评价（处理表单提交）
const submitEvaluation = () => {
  handleSubmitEvaluation()
}

onMounted(async () => {
  await tasks.loadTask(taskId.value)
})
</script>

<style scoped>
.evaluation-page {
  max-width: 800px;
  margin: 0 auto;
}

.task-info {
  margin-bottom: 1.5rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.task-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.evaluation-form {
  padding: 2rem;
}

.evaluation-form h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.evaluation-target {
  margin-bottom: 1.5rem;
  color: var(--text-secondary);
}

.score-label {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.evaluation-form .n-form-item {
  margin-bottom: 1.5rem;
}

.evaluation-form .n-form-item:last-child {
  margin-bottom: 0;
}
</style>
