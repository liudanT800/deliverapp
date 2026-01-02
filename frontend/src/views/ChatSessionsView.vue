<template>
  <div class="chat-sessions-page">
    <n-page-header>
      <template #title>
        我的沟通
      </template>
      <template #subtitle>
        查看所有任务相关的沟通记录
      </template>
    </n-page-header>

    <section class="card">
      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
        <p>加载会话中...</p>
      </div>
      <div v-else-if="sessions.length === 0" class="empty-state">
        <n-empty description="暂无沟通记录">
          <template #extra>
            <p>接受任务后可以与发布者进行沟通</p>
            <n-button type="primary" @click="router.push('/')">
              浏览任务
            </n-button>
          </template>
        </n-empty>
      </div>
      <div v-else class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.taskId"
          class="session-item"
          @click="openChat(session.taskId)"
        >
          <div class="session-avatar">
            <n-avatar round :size="48">
              {{ session.otherParty.fullName.slice(0, 1) }}
            </n-avatar>
          </div>

          <div class="session-content">
            <div class="session-header">
              <h4>{{ session.taskTitle }}</h4>
              <span class="session-time">
                {{ session.lastMessageTime ? formatTime(session.lastMessageTime) : '暂无消息' }}
              </span>
            </div>

            <div class="session-meta">
              <span class="other-party">与 {{ session.otherParty.fullName }} 沟通</span>
            </div>

            <div v-if="session.lastMessage" class="last-message">
              {{ session.lastMessage.length > 50 ? session.lastMessage.slice(0, 50) + '...' : session.lastMessage }}
            </div>
          </div>

          <div class="session-arrow">
            <n-icon size="20" color="var(--text-secondary)">
              <ChevronForward />
            </n-icon>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTaskStore } from '../stores/tasks'
import { apiService as api } from '../api/api-service'
import { type ChatSession, type BackendChatSession } from '../api/chat'
import { ChevronForward } from '@vicons/ionicons5'
import { useMessage } from 'naive-ui'

const router = useRouter()
const auth = useAuthStore()
const tasks = useTaskStore()
const message = useMessage()

const sessions = ref<ChatSession[]>([])
const loading = ref(false)

// 格式化时间
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 一分钟内
  if (diff < 60000) {
    return '刚刚'
  }

  // 一小时内
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }

  // 今天
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }

  // 更早
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

// 加载会话列表
const loadSessions = async () => {
  loading.value = true
  try {
    const response = await api.chat.sessions()
    console.log('API response:', response)
    console.log('Response success:', response.success)
    console.log('Response data:', response.data)
    console.log('Response data type:', typeof response.data)
    console.log('Is array?', Array.isArray(response.data))

    if (response.success && response.data && response.data.success && Array.isArray(response.data.data)) {
      // 确保data是数组
      let backendSessions: BackendChatSession[] = response.data.data as BackendChatSession[]
      console.log('Backend sessions:', backendSessions)

      console.log('Final backend sessions:', backendSessions)
      const convertedSessions: ChatSession[] = []

      for (const session of backendSessions) {
        console.log('Processing session:', session)
        console.log('session.taskId:', session.taskId)
        console.log('session.taskId type:', typeof session.taskId)

        // 验证taskId
        if (!session.taskId || typeof session.taskId !== 'number') {
          console.warn('Invalid taskId in session:', session)
          continue
        }

        // 获取任务信息
        let taskTitle = '未知任务'
        try {
          console.log('Fetching task info for taskId:', session.taskId)
          const taskResponse = await api.tasks.get(session.taskId)
          console.log('Task response:', taskResponse)
          if (taskResponse.success && taskResponse.data) {
            taskTitle = taskResponse.data.title
          }
        } catch (error) {
          console.warn(`获取任务${session.taskId}信息失败:`, error)
        }

        convertedSessions.push({
          taskId: session.taskId,
          taskTitle,
          lastMessage: session.lastMessage,
          lastMessageTime: session.lastMessageTime,
          unreadCount: session.unreadCount,
          otherParty: {
            id: session.otherUser.id,
            fullName: session.otherUser.fullName
          }
        })
      }

      sessions.value = convertedSessions
    } else {
      message.error(response.message || '加载会话列表失败')
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
    message.error('加载会话列表失败')
  } finally {
    loading.value = false
  }
}

// 打开聊天
const openChat = (taskId: number) => {
  console.log('Opening chat for taskId:', taskId)
  console.log('taskId type:', typeof taskId)
  console.log('taskId is valid:', !isNaN(taskId) && taskId > 0)

  if (!taskId || isNaN(taskId) || taskId <= 0) {
    console.error('Invalid taskId for chat:', taskId)
    return
  }

  router.push(`/chat/${taskId}`)
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.chat-sessions-page {
  max-width: 800px;
  margin: 0 auto;
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

.sessions-list {
  display: flex;
  flex-direction: column;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.session-item:hover {
  background: var(--bg-tertiary);
}

.session-item:last-child {
  border-bottom: none;
}

.session-avatar {
  position: relative;
  margin-right: 1rem;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.25rem;
}

.session-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 60%;
}

.session-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.session-meta {
  margin-bottom: 0.25rem;
}

.other-party {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.last-message {
  font-size: 0.9rem;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-arrow {
  margin-left: 1rem;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .session-item {
    padding: 0.75rem;
  }

  .session-header h4 {
    max-width: 50%;
  }
}
</style>
