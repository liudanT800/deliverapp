<template>
  <div class="chat-page">
    <n-page-header>
      <template #title>
        任务沟通
      </template>
      <template #subtitle>
        与任务参与者进行留言式沟通
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

    <!-- 聊天区域 -->
    <section class="card chat-section">
      <!-- WebSocket连接状态 -->
      <div class="connection-status" :class="{ connected: websocketConnected }">
        <n-icon size="16">
          <Wifi v-if="websocketConnected" />
          <WifiOutline v-else />
        </n-icon>
        <span>{{ websocketConnected ? '实时连接' : '连接中...' }}</span>
      </div>

      <div class="chat-messages" ref="messagesContainer">

        <div v-if="loading" class="loading-messages">
          <n-spin size="small" />
          <span>加载消息中...</span>
        </div>
        <div v-else-if="messages.length === 0" class="empty-messages">
          <n-empty description="暂无消息记录">
            <template #extra>
              <p>开始与对方沟通吧！</p>
            </template>
          </n-empty>
        </div>
        <div v-else class="messages-list">
          <div v-for="message in messages" :key="message.id"
            :class="['message-item', message.senderId === currentUser?.id ? 'own' : 'other']">
            <div class="message-header">
              <span class="sender-name">{{ message.senderId === currentUser?.id ? '我' : '对方' }}</span>
              <span class="message-time">{{ formatTime(message.createdAt) }}</span>
            </div>
            <div class="message-content">
              {{ message.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- 发送消息区域 -->
      <div class="message-input">
        <n-form :model="messageForm" @submit.prevent="handleSendMessage">
          <n-form-item>
            <n-input v-model:value="messageForm.content" placeholder="输入留言内容..." :maxlength="500" show-count clearable
              @keydown.enter.prevent="handleSendMessage">
              <template #suffix>
                <n-button type="primary" :loading="sending" :disabled="!messageForm.content.trim()"
                  @click="handleSendMessage">
                  发送
                </n-button>
              </template>
            </n-input>
          </n-form-item>
        </n-form>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTaskStore, TASK_CATEGORY_LABELS } from '../stores/tasks'
import { apiService as api } from '../api/api-service'
import { type Message, type SendMessagePayload } from '../api/chat'
import { useMessage } from 'naive-ui'
import { Wifi, WifiOutline } from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tasks = useTaskStore()
const message = useMessage()

// 使用计算属性来响应路由参数变化
const taskId = computed(() => {
  const id = route.params.id
  return Number(id) || 0
})
const task = computed(() => tasks.currentTask)
const messages = ref<Message[]>([])
const loading = ref(false)
const sending = ref(false)
const messagesContainer = ref<HTMLElement>()

// WebSocket相关状态
const websocket = ref<WebSocket | null>(null)
const websocketConnected = ref(false)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5

const messageForm = ref({
  content: ''
})

const currentUser = computed(() => auth.user)

// 任务分类标签
const categoryLabel = (category: string | undefined) => {
  return category ? (TASK_CATEGORY_LABELS[category] || category) : '未知'
}

// 格式化时间
const formatTime = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateStr)
      return '时间未知'
    }
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Date formatting error:', error, 'for dateStr:', dateStr)
    return '时间未知'
  }
}

// 加载聊天记录
const loadMessages = async () => {
  if (!taskId.value) return

  loading.value = true
  try {
    const response = await api.chat.history(taskId.value)
    if (response.success && response.data && response.data.success && Array.isArray(response.data.data)) {
      messages.value = response.data.data
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载聊天记录失败:', error)
    message.error('加载聊天记录失败')
  } finally {
    loading.value = false
  }
}

// 发送消息
const handleSendMessage = async () => {
  // 验证用户认证状态
  if (!auth.isAuthenticated || !currentUser.value) {
    message.error('请先登录')
    router.push('/login')
    return
  }

  if (!messageForm.value.content.trim() || !task.value) {
    return
  }

  // 确定接收者：优先使用ID字段，如果没有则从对象中获取
  const currentUserId = currentUser.value.id
  console.log('Current user ID:', currentUserId)
  const taskCreatedById = task.value.createdById || task.value.createdBy?.id
  const taskAssignedToId = task.value.assignedToId || task.value.assignedTo?.id

  // 确定接收者：如果当前用户是任务创建者，发送给接单者；反之亦然
  const receiverId = taskCreatedById === currentUserId
    ? taskAssignedToId
    : taskCreatedById

  if (!receiverId) {
    console.error('无法确定消息接收者:', {
      currentUserId,
      taskCreatedById,
      taskAssignedToId,
      taskData: task.value
    })
    message.error('无法确定消息接收者')
    return
  }

  const payload: SendMessagePayload = {
    taskId: taskId.value,
    receiverId: receiverId,
    content: messageForm.value.content.trim()
  }

  sending.value = true
  try {
    const response = await api.chat.send(payload)
    if (response.success && response.data) {
      // 发送成功后重新获取聊天记录，确保显示最新的消息
      await loadMessages()
      messageForm.value.content = ''
      message.success('消息发送成功')
    } else {
      message.error(response.message || '发送消息失败')
    }
  } catch (error: any) {
    console.error('发送消息失败:', error)
    message.error(error.message || '发送消息失败')
  } finally {
    sending.value = false
  }
}

// WebSocket连接
const connectWebSocket = () => {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    return // 已经连接
  }

  const token = localStorage.getItem('token')
  if (!token) {
    console.warn('没有token，跳过WebSocket连接')
    return
  }

  try {
    const wsUrl = `ws://localhost:9800/api/chat/ws/${taskId.value}?token=${token}`
    console.log('尝试连接WebSocket:', wsUrl)
    websocket.value = new WebSocket(wsUrl)

    websocket.value.onopen = () => {
      console.log('WebSocket连接成功', `ws://localhost:9800/api/chat/ws/${taskId.value}`)
      websocketConnected.value = true
      reconnectAttempts.value = 0
    }

    websocket.value.onmessage = (event) => {
      console.log('收到WebSocket消息:', event.data)
      try {
        const data = JSON.parse(event.data)
        console.log('解析后的消息:', data)
        if (data.type === 'new_message') {
          const newMessage = data.data as Message
          console.log('新消息:', newMessage)
          console.log('当前任务ID:', taskId.value, '消息任务ID:', newMessage.taskId)
          console.log('当前用户ID:', currentUser.value?.id, '发送者ID:', newMessage.senderId)

          // 检查是否是当前任务的消息且不是自己发的
          if (newMessage.taskId === taskId.value && newMessage.senderId !== currentUser.value?.id) {
            console.log('添加新消息到列表')
            messages.value.push(newMessage)
            nextTick(() => scrollToBottom())
            // 可以添加新消息提示音或其他通知
          } else {
            console.log('消息被过滤，原因:', {
              taskMatch: newMessage.taskId === taskId.value,
              notSelf: newMessage.senderId !== currentUser.value?.id
            })
          }
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }

    websocket.value.onclose = () => {
      console.log('WebSocket连接关闭')
      websocketConnected.value = false
      websocket.value = null

      // 自动重连逻辑
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        console.log(`尝试重连WebSocket (${reconnectAttempts.value}/${maxReconnectAttempts})`)
        setTimeout(() => connectWebSocket(), 2000 * reconnectAttempts.value) // 递增延迟
      } else {
        console.warn('WebSocket重连次数达到上限，停止重连')
      }
    }

    websocket.value.onerror = (error) => {
      console.error('WebSocket连接错误:', error)
    }
  } catch (error) {
    console.error('创建WebSocket连接失败:', error)
  }
}

// 断开WebSocket连接
const disconnectWebSocket = () => {
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
    websocketConnected.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}


// 页面可见性变化处理（用于WebSocket重连）
const handleVisibilityChange = () => {
  if (document.hidden) {
    // 页面不可见时，可以选择断开WebSocket节省资源
    disconnectWebSocket()
  } else {
    // 页面重新可见时，重新连接WebSocket
    connectWebSocket()
  }
}

// 监听路由参数变化
watch(() => route.params.id, async (newId) => {
  if (newId && !isNaN(Number(newId))) {
    await tasks.loadTask(Number(newId))
    await loadMessages()
    connectWebSocket()
  }
})

onMounted(async () => {
  // 等待认证信息加载完成
  if (auth.isAuthenticated && !auth.user) {
    await auth.getCurrentUser()
  }

  // 验证用户认证状态
  if (!auth.isAuthenticated || !auth.user) {
    message.error('请先登录')
    router.push('/login')
    return
  }

  // 验证路由参数
  if (!taskId.value || isNaN(taskId.value)) {
    message.error('无效的任务ID')
    router.push('/chat-sessions')
    return
  }

  // 加载任务数据
  await tasks.loadTask(taskId.value)
  await loadMessages()
  connectWebSocket()

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  disconnectWebSocket()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.chat-page {
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

.chat-section {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 300px);
  min-height: 400px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.connection-status.connected {
  color: var(--success-color);
}

.connection-status .n-icon {
  color: currentColor;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.loading-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.empty-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  max-width: 70%;
  padding: 0.75rem;
  border-radius: var(--radius-medium);
  position: relative;
}

.message-item.own {
  align-self: flex-end;
  background: var(--primary-color);
  color: white;
}

.message-item.other {
  align-self: flex-start;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  opacity: 0.8;
}

.sender-name {
  font-weight: 500;
}

.message-time {
  font-size: 0.75rem;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-input {
  padding: 1rem;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.message-input .n-form-item {
  margin-bottom: 0;
}

.message-input .n-input {
  background: white;
}
</style>
