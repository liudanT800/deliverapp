/**
 * Payment API 接口
 */

export interface WalletInfo {
  userId: number
  balance: number
  updatedAt: string
}

export interface Transaction {
  id: number
  userId: number
  amount: number
  type: 'deposit' | 'withdraw' | 'payment' | 'reward'
  relatedId?: number
  description?: string
  createdAt: string
}

export interface RechargePayload {
  amount: number
  description?: string
}

export interface PaymentPayload {
  taskId: number
  amount: number
}

export interface SettlementPayload {
  taskId: number
  amount: number
}

// 查询余额
export async function getBalance(): Promise<{ success: boolean; message: string; data?: WalletInfo }> {
  const response = await fetch('/api/payment/balance', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '查询余额失败')
  }

  return result
}

// 模拟充值
export async function recharge(payload: RechargePayload): Promise<{ success: boolean; message: string; data?: WalletInfo }> {
  const response = await fetch('/api/payment/recharge', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(payload)
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '充值失败')
  }

  return result
}

// 获取交易流水
export async function getTransactions(): Promise<{ success: boolean; message: string; data?: Transaction[] }> {
  const response = await fetch('/api/payment/transactions', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '获取交易记录失败')
  }

  return result
}

// 支付任务赏金
export async function payForTask(payload: PaymentPayload): Promise<{ success: boolean; message: string; data?: Transaction }> {
  const response = await fetch('/api/payment/pay', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(payload)
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '支付失败')
  }

  return result
}

// 结算赏金给接单人
export async function settlePayment(payload: SettlementPayload): Promise<{ success: boolean; message: string; data?: Transaction }> {
  const response = await fetch('/api/payment/settle', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(payload)
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || '结算失败')
  }

  return result
}

