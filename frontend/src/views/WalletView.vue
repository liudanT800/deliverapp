<template>
  <div class="wallet-page">
    <n-page-header>
      <template #title>
        我的钱包
      </template>
      <template #subtitle>
        管理您的余额和交易记录
      </template>
    </n-page-header>

    <!-- 余额卡片 -->
    <section class="card balance-card">
      <div class="balance-header">
        <div>
          <h3>当前余额</h3>
          <div class="balance-amount">
            <span class="currency">¥</span>
            <span class="amount">{{ wallet?.balance?.toFixed(2) || '0.00' }}</span>
          </div>
        </div>
        <n-button type="primary" @click="showRechargeModal = true">
          充值
        </n-button>
      </div>
    </section>

    <!-- 快捷操作 -->
    <section class="card quick-actions">
      <h3>快捷操作</h3>
      <div class="actions-grid">
        <n-button
          type="info"
          size="large"
          @click="showRechargeModal = true"
        >
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          充值
        </n-button>
        <n-button
          type="warning"
          size="large"
          @click="showTransactions = !showTransactions"
        >
          <template #icon>
            <n-icon><List /></n-icon>
          </template>
          交易记录
        </n-button>
      </div>
    </section>

    <!-- 交易记录 -->
    <section v-if="showTransactions" class="card transactions-section">
      <div class="section-header">
        <h3>交易记录</h3>
          <n-button text @click="refreshTransactions">
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            刷新
          </n-button>
      </div>

      <div v-if="transactionsLoading" class="loading-state">
        <n-spin size="large" />
        <p>加载交易记录中...</p>
      </div>
      <div v-else-if="transactions.length === 0" class="empty-state">
        <n-empty description="暂无交易记录">
          <template #extra>
            <p>完成任务后将有交易记录</p>
          </template>
        </n-empty>
      </div>
      <div v-else class="transactions-list">
        <div
          v-for="transaction in transactions"
          :key="transaction.id"
          class="transaction-item"
        >
          <div class="transaction-icon">
            <n-icon
              :color="getTransactionIconColor(transaction.type)"
              size="24"
            >
              <component :is="getTransactionIcon(transaction.type)" />
            </n-icon>
          </div>

          <div class="transaction-content">
            <div class="transaction-header">
              <span class="transaction-type">{{ getTransactionTypeLabel(transaction.type) }}</span>
              <span class="transaction-amount" :class="getAmountClass(transaction.type)">
                {{ getAmountPrefix(transaction.type) }}{{ Math.abs(transaction.amount).toFixed(2) }}
              </span>
            </div>
            <div class="transaction-meta">
              <span class="transaction-desc">{{ transaction.description || '无描述' }}</span>
              <span class="transaction-time">{{ formatTime(transaction.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>

  <!-- 充值模态框 -->
  <n-modal
    v-model:show="showRechargeModal"
    preset="card"
    title="充值"
    size="small"
  >
    <n-form :model="rechargeForm" @submit.prevent="handleRecharge">
      <n-form-item label="充值金额" required>
        <n-input-number
          v-model:value="rechargeForm.amount"
          :min="1"
          :max="10000"
          :precision="2"
          placeholder="输入充值金额"
          style="width: 100%"
        />
      </n-form-item>

      <n-form-item label="备注">
        <n-input
          v-model:value="rechargeForm.description"
          placeholder="可选备注信息"
          maxlength="100"
        />
      </n-form-item>

      <n-form-item>
        <n-space>
          <n-button
            type="primary"
            :loading="recharging"
            :disabled="!rechargeForm.amount || rechargeForm.amount <= 0"
            @click="handleRecharge"
          >
            确认充值
          </n-button>
          <n-button @click="showRechargeModal = false">
            取消
          </n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { getBalance, getTransactions, recharge, type WalletInfo, type Transaction, type RechargePayload } from '../api/payment'
import {
  Add,
  List,
  Refresh,
  TrendingUp,
  TrendingDown,
  Cash
} from '@vicons/ionicons5'

const message = useMessage()

const wallet = ref<WalletInfo | null>(null)
const transactions = ref<Transaction[]>([])
const showTransactions = ref(false)
const transactionsLoading = ref(false)
const showRechargeModal = ref(false)
const recharging = ref(false)

const rechargeForm = ref({
  amount: 0,
  description: ''
})

// 格式化时间
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取交易类型标签
const getTransactionTypeLabel = (type: string) => {
  const labels = {
    deposit: '充值',
    withdraw: '提现',
    payment: '支付',
    reward: '赏金'
  }
  return labels[type as keyof typeof labels] || type
}

// 获取金额前缀
const getAmountPrefix = (type: string) => {
  return type === 'deposit' || type === 'reward' ? '+' : '-'
}

// 获取金额样式类
const getAmountClass = (type: string) => {
  return type === 'deposit' || type === 'reward' ? 'income' : 'expense'
}

// 获取交易图标
const getTransactionIcon = (type: string) => {
  const icons = {
    deposit: Add,
    withdraw: TrendingDown,
    payment: Cash,
    reward: TrendingUp
  }
  return icons[type as keyof typeof icons] || DollarIcon
}

// 获取交易图标颜色
const getTransactionIconColor = (type: string) => {
  const colors = {
    deposit: '#10b981',  // 绿色
    withdraw: '#f59e0b', // 橙色
    payment: '#ef4444',  // 红色
    reward: '#3b82f6'    // 蓝色
  }
  return colors[type as keyof typeof colors] || '#6b7280'
}

// 加载余额
const loadBalance = async () => {
  try {
    const response = await getBalance()
    if (response.success && response.data) {
      wallet.value = response.data
    }
  } catch (error) {
    console.error('加载余额失败:', error)
  }
}

// 加载交易记录
const loadTransactions = async () => {
  transactionsLoading.value = true
  try {
    const response = await getTransactions()
    if (response.success && response.data) {
      transactions.value = response.data
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
  } finally {
    transactionsLoading.value = false
  }
}

// 刷新交易记录
const refreshTransactions = () => {
  loadTransactions()
}

// 处理充值
const handleRecharge = async () => {
  if (!rechargeForm.value.amount || rechargeForm.value.amount <= 0) return

  const payload: RechargePayload = {
    amount: rechargeForm.value.amount,
    description: rechargeForm.value.description || undefined
  }

  recharging.value = true
  try {
    const response = await recharge(payload)
    if (response.success) {
      message.success('充值成功！')
      showRechargeModal.value = false
      rechargeForm.value = { amount: 0, description: '' }
      await loadBalance() // 刷新余额
    } else {
      message.error(response.message || '充值失败')
    }
  } catch (error: any) {
    message.error(error.message || '充值失败')
  } finally {
    recharging.value = false
  }
}

onMounted(() => {
  loadBalance()
})
</script>

<style scoped>
.wallet-page {
  max-width: 800px;
  margin: 0 auto;
}

.balance-card {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  margin-bottom: 1.5rem;
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-amount {
  display: flex;
  align-items: baseline;
  margin-top: 0.5rem;
}

.currency {
  font-size: 1.5rem;
  margin-right: 0.25rem;
}

.amount {
  font-size: 2.5rem;
  font-weight: 700;
}

.quick-actions {
  margin-bottom: 1.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.transactions-section {
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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

.transactions-list {
  display: flex;
  flex-direction: column;
}

.transaction-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.transaction-item:last-child {
  border-bottom: none;
}

.transaction-icon {
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.transaction-content {
  flex: 1;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.transaction-type {
  font-weight: 500;
  color: var(--text-primary);
}

.transaction-amount {
  font-weight: 600;
}

.transaction-amount.income {
  color: var(--success-color);
}

.transaction-amount.expense {
  color: var(--error-color);
}

.transaction-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transaction-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.transaction-time {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

@media (max-width: 768px) {
  .balance-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .transaction-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .transaction-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
