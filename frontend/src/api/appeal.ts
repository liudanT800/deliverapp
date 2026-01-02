/**
 * Appeal API 接口
 */

export interface Appeal {
  id: number
  taskId: number
  creatorId: number
  reason: string
  status: 'pending' | 'processing' | 'resolved' | 'rejected'
  adminReply?: string
  createdAt: string
  updatedAt: string
  task?: {
    id: number
    title: string
  }
}

export interface CreateAppealPayload {
  taskId: number
  reason: string
}

// 获取申诉列表
export async function getAppeals(): Promise<{ success: boolean; message: string; data?: Appeal[] }> {
  const response = await fetch('/api/appeal/my', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '获取申诉列表失败')
  }

  return result
}

// 创建申诉
export async function createAppeal(payload: CreateAppealPayload): Promise<{ success: boolean; message: string; data?: Appeal }> {
  const response = await fetch('/api/appeal/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(payload)
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '创建申诉失败')
  }

  return result
}

// 获取申诉详情
export async function getAppealDetail(appealId: number): Promise<{ success: boolean; message: string; data?: Appeal }> {
  const response = await fetch(`/api/appeal/${appealId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '获取申诉详情失败')
  }

  return result
}
