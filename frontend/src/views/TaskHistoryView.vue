<template>
  <div class="history-page">
    <n-page-header @back="goBack">
      <template #title>
        任务历史记录
      </template>
      <template #subtitle>
        查看任务的所有状态变更历史
      </template>
    </n-page-header>

    <section class="card filters">
      <n-form inline :model="filters" label-placement="left">
        <n-form-item label="任务ID">
          <n-input v-model:value="filters.taskId" placeholder="输入任务ID" />
        </n-form-item>
        <n-form-item label="操作人">
          <n-input v-model:value="filters.operator" placeholder="输入操作人姓名" />
        </n-form-item>
        <n-form-item label="日期范围">
          <n-date-picker v-model:value="filters.dateRange" type="daterange" clearable />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" @click="search">搜索</n-button>
          <n-button @click="resetFilters" style="margin-left: 10px;">重置</n-button>
        </n-form-item>
      </n-form>
    </section>

    <section class="card">
      <n-data-table
        :columns="columns"
        :data="filteredHistory"
        :loading="loading"
        :pagination="pagination"
        striped
      />
      <n-empty v-if="!loading && filteredHistory.length === 0" description="暂无历史记录">
        <template #extra>
          <div class="empty-state-actions">
            <n-button @click="resetFilters">重置筛选</n-button>
            <n-button type="primary" @click="search">重新搜索</n-button>
          </div>
          <div class="empty-state-tips">
            <h4>提示：</h4>
            <ul>
              <li>调整筛选条件可能会发现更多记录</li>
              <li>任务完成后会生成历史记录</li>
            </ul>
          </div>
        </template>
      </n-empty>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NPageHeader, 
  NForm, 
  NFormItem, 
  NInput, 
  NDatePicker, 
  NButton, 
  NDataTable 
} from 'naive-ui'

const router = useRouter()
const loading = ref(false)

// 筛选条件
const filters = ref({
  taskId: '',
  operator: '',
  dateRange: null as [number, number] | null
})

// 历史记录数据（模拟）
const historyData = ref([
  {
    id: 1,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '张三',
    operatorRole: '用户',
    action: '创建任务',
    status: 'pending',
    remark: '发布了新的代取快递任务',
    timestamp: '2025-05-01T10:00:00Z'
  },
  {
    id: 2,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '李四',
    operatorRole: '用户',
    action: '接单',
    status: 'accepted',
    remark: '我正好顺路，可以帮忙取快递',
    timestamp: '2025-05-01T11:30:00Z'
  },
  {
    id: 3,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '李四',
    operatorRole: '用户',
    action: '更新状态',
    status: 'picked',
    remark: '已取到快递，准备送往目的地',
    timestamp: '2025-05-01T12:15:00Z'
  },
  {
    id: 4,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '李四',
    operatorRole: '用户',
    action: '更新状态',
    status: 'delivering',
    remark: '正在送往图书馆',
    timestamp: '2025-05-01T12:30:00Z'
  },
  {
    id: 5,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '张三',
    operatorRole: '用户',
    action: '确认完成',
    status: 'confirming',
    remark: '已收到快递，请确认任务完成',
    timestamp: '2025-05-01T12:45:00Z'
  },
  {
    id: 6,
    taskId: 1001,
    taskTitle: '代取快递',
    operator: '系统',
    operatorRole: '系统',
    action: '完成任务',
    status: 'completed',
    remark: '双方已确认，任务完成，酬金已结算',
    timestamp: '2025-05-01T13:00:00Z'
  }
])

// 分页配置
const pagination = {
  pageSize: 10
}

// 筛选后的历史记录
const filteredHistory = computed(() => {
  let result = [...historyData.value]
  
  // 根据任务ID筛选
  if (filters.value.taskId) {
    const taskId = parseInt(filters.value.taskId)
    result = result.filter(item => item.taskId === taskId)
  }
  
  // 根据操作人筛选
  if (filters.value.operator) {
    const operator = filters.value.operator.toLowerCase()
    result = result.filter(item => 
      item.operator.toLowerCase().includes(operator)
    )
  }
  
  // 根据日期范围筛选
  if (filters.value.dateRange) {
    const [start, end] = filters.value.dateRange
    const startDate = new Date(start)
    const endDate = new Date(end)
    
    result = result.filter(item => {
      const itemDate = new Date(item.timestamp)
      return itemDate >= startDate && itemDate <= endDate
    })
  }
  
  return result
})

// 表格列定义
const columns = [
  {
    title: '任务ID',
    key: 'taskId',
    width: 100
  },
  {
    title: '任务标题',
    key: 'taskTitle',
    ellipsis: true
  },
  {
    title: '操作人',
    key: 'operator',
    width: 120
  },
  {
    title: '角色',
    key: 'operatorRole',
    width: 100
  },
  {
    title: '操作',
    key: 'action',
    width: 120
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render(row: any) {
      return h('span', { style: { fontWeight: 'bold' } }, getStatusText(row.status))
    }
  },
  {
    title: '备注',
    key: 'remark',
    ellipsis: true
  },
  {
    title: '时间',
    key: 'timestamp',
    width: 180,
    render(row: any) {
      return new Date(row.timestamp).toLocaleString('zh-CN')
    }
  }
]

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待接单',
    accepted: '已接单',
    picked: '已取件',
    delivering: '派送中',
    confirming: '待确认',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 搜索
const search = () => {
  // 实际应用中这里会调用API获取数据
  console.log('搜索条件:', filters.value)
}

// 重置筛选条件
const resetFilters = () => {
  filters.value.taskId = ''
  filters.value.operator = ''
  filters.value.dateRange = null
}

// 返回上一页
const goBack = () => {
  router.back()
}

onMounted(() => {
  // 页面加载时获取历史记录数据
  // fetchHistoryData()
})
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  padding: 1.5rem;
}

.filters {
  background: var(--bg-tertiary);
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