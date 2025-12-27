<template>
  <div class="management-page">
    <header class="card">
      <div>
        <h2>任务管理</h2>
        <p>管理所有任务的状态和流程</p>
      </div>
      <n-button @click="refreshTasks">刷新</n-button>
    </header>

    <section class="card">
      <n-tabs type="segment" v-model:value="activeTab">
        <n-tab-pane name="all" tab="全部任务">
          <n-spin :show="tasks.loading">
            <TaskList v-if="allTasks.length > 0" :tasks="allTasks" @task-updated="handleTaskUpdated" />
            <n-empty v-else description="暂无任务">
              <template #extra>
                <div class="empty-state-actions">
                  <n-button @click="refreshTasks">刷新列表</n-button>
                  <n-button type="primary" @click="router.push('/tasks/create')">发布新任务</n-button>
                </div>
                <div class="empty-state-tips">
                  <h4>提示：</h4>
                  <ul>
                    <li>任务发布后会显示在这里</li>
                    <li>可以刷新列表获取最新数据</li>
                  </ul>
                </div>
              </template>
            </n-empty>
          </n-spin>
        </n-tab-pane>
        <n-tab-pane name="pending" tab="待接单">
          <n-spin :show="tasks.loading">
            <TaskList v-if="pendingTasks.length > 0" :tasks="pendingTasks" @task-updated="handleTaskUpdated" />
            <n-empty v-else description="暂无待接单任务">
              <template #extra>
                <div class="empty-state-actions">
                  <n-button @click="refreshTasks">刷新列表</n-button>
                  <n-button type="primary" @click="router.push('/tasks/create')">发布新任务</n-button>
                </div>
                <div class="empty-state-tips">
                  <h4>提示：</h4>
                  <ul>
                    <li>新发布的任务会显示在这里</li>
                    <li>可以刷新列表获取最新数据</li>
                  </ul>
                </div>
              </template>
            </n-empty>
          </n-spin>
        </n-tab-pane>
        <n-tab-pane name="in-progress" tab="进行中">
          <n-spin :show="tasks.loading">
            <TaskList v-if="inProgressTasks.length > 0" :tasks="inProgressTasks" @task-updated="handleTaskUpdated" />
            <n-empty v-else description="暂无进行中的任务">
              <template #extra>
                <div class="empty-state-actions">
                  <n-button @click="refreshTasks">刷新列表</n-button>
                </div>
                <div class="empty-state-tips">
                  <h4>提示：</h4>
                  <ul>
                    <li>接单后的任务会显示在这里</li>
                    <li>可以刷新列表获取最新数据</li>
                  </ul>
                </div>
              </template>
            </n-empty>
          </n-spin>
        </n-tab-pane>
        <n-tab-pane name="completed" tab="已完成">
          <n-spin :show="tasks.loading">
            <TaskList v-if="completedTasks.length > 0" :tasks="completedTasks" @task-updated="handleTaskUpdated" />
            <n-empty v-else description="暂无已完成任务">
              <template #extra>
                <div class="empty-state-actions">
                  <n-button @click="refreshTasks">刷新列表</n-button>
                </div>
                <div class="empty-state-tips">
                  <h4>提示：</h4>
                  <ul>
                    <li>完成的任务会显示在这里</li>
                    <li>可以刷新列表获取最新数据</li>
                  </ul>
                </div>
              </template>
            </n-empty>
          </n-spin>
        </n-tab-pane>
      </n-tabs>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore, TASK_STATUS_LABELS } from '../stores/tasks'
import TaskList from '../components/TaskList.vue'

const router = useRouter()
const tasks = useTaskStore()
const activeTab = ref('all')

// 刷新任务列表
function refreshTasks() {
  tasks.loadTasks()
}

// 处理任务更新事件
function handleTaskUpdated() {
  tasks.loadTasks()
}

// 所有任务
const allTasks = computed(() => tasks.items)

// 待接单任务
const pendingTasks = computed(() => 
  tasks.items.filter(task => task.status === 'pending')
)

// 进行中任务
const inProgressTasks = computed(() => 
  tasks.items.filter(task => 
    ['accepted', 'picked', 'delivering', 'confirming'].includes(task.status)
  )
)

// 已完成任务
const completedTasks = computed(() => 
  tasks.items.filter(task => 
    ['completed', 'cancelled'].includes(task.status)
  )
)

onMounted(async () => {
  await tasks.loadTasks()
})
</script>

<style scoped>
.management-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  padding: 1.5rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
</style>