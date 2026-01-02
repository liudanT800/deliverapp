/**
 * Evaluation API 接口
 */

export interface Evaluation {
  id: number
  taskId: number
  evaluatorId: number
  evaluateeId: number
  score: number
  comment?: string
  createdAt: string
  evaluator?: {
    id: number
    fullName: string
  }
  evaluatee?: {
    id: number
    fullName: string
  }
  task?: {
    id: number
    title: string
  }
}

export interface UserEvaluationStats {
  userId: number
  averageScore: number
  totalEvaluations: number
  evaluations: Evaluation[]
}

export interface TaskEvaluationInfo {
  taskId: number
  evaluations: Evaluation[]
  averageScore?: number
}

export interface SubmitEvaluationPayload {
  taskId: number
  evaluateeId: number
  score: number
  comment?: string
}

// 提交评价
export async function submitEvaluation(payload: SubmitEvaluationPayload): Promise<{ success: boolean; message: string; data?: Evaluation }> {
  const response = await fetch('/api/evaluation/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(payload)
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '提交评价失败')
  }

  return result
}

// 获取用户评价列表及平均分
export async function getUserEvaluations(userId: number): Promise<{ success: boolean; message: string; data?: UserEvaluationStats }> {
  const response = await fetch(`/api/evaluation/user/${userId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '获取用户评价失败')
  }

  return result
}

// 获取任务评价信息
export async function getTaskEvaluations(taskId: number): Promise<{ success: boolean; message: string; data?: TaskEvaluationInfo }> {
  const response = await fetch(`/api/evaluation/task/${taskId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '获取任务评价失败')
  }

  return result
}

