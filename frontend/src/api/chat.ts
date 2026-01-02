/**
 * Chat API 接口
 */

export interface Message {
  id: number
  taskId: number
  senderId: number
  receiverId: number
  content: string
  isRead: boolean
  createdAt: string
  sender?: {
    id: number
    fullName: string
  }
}

export interface ChatSession {
  taskId: number
  taskTitle: string
  lastMessage?: string
  lastMessageTime?: string
  unreadCount: number
  otherParty: {
    id: number
    fullName: string
  }
}

// 后端实际返回的数据结构（驼峰命名）
export interface BackendChatSession {
  taskId: number
  otherUser: {
    id: number
    fullName: string
  }
  lastMessage?: string
  lastMessageTime?: string
  unreadCount: number
}

export interface SendMessagePayload {
  taskId: number
  receiverId: number
  content: string
}

// 发送消息
export async function sendMessage(payload: SendMessagePayload): Promise<{ success: boolean; message: string; data?: Message }> {
  try {
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(payload)
    })

    let result
    try {
      result = await response.json()
    } catch (jsonError) {
      console.error('JSON解析失败:', jsonError)
      throw new Error('服务器响应格式错误')
    }

    if (!response.ok) {
      throw new Error(result.message || '发送消息失败')
    }

    return result
  } catch (error) {
    console.error('发送消息API调用失败:', error)
    throw error
  }
}

// 获取聊天记录
export async function getChatHistory(taskId: number): Promise<{ success: boolean; message: string; data?: Message[] }> {
  try {
    const response = await fetch(`/api/chat/history/${taskId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    let result
    try {
      result = await response.json()
    } catch (jsonError) {
      console.error('JSON解析失败:', jsonError)
      throw new Error('服务器响应格式错误')
    }

    if (!response.ok) {
      throw new Error(result.message || '获取聊天记录失败')
    }

    return result
  } catch (error) {
    console.error('获取聊天记录API调用失败:', error)
    throw error
  }
}

// 获取会话列表
export async function getChatSessions(): Promise<{ success: boolean; message: string; data?: ChatSession[] }> {
  try {
    const response = await fetch('/api/chat/sessions', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    let result
    try {
      result = await response.json()
    } catch (jsonError) {
      console.error('JSON解析失败:', jsonError)
      throw new Error('服务器响应格式错误')
    }

    if (!response.ok) {
      throw new Error(result.message || '获取会话列表失败')
    }

    return result
  } catch (error) {
    console.error('获取会话列表API调用失败:', error)
    throw error
  }
}

