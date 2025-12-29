<template>
  <div class="user-management-page">
    <n-page-header>
      <template #title>
        用户管理
      </template>
      <template #subtitle>
        管理平台用户信息和权限
      </template>
    </n-page-header>

    <section class="card">
      <div class="toolbar">
        <n-input v-model:value="searchKeyword" placeholder="搜索用户..." class="search-input">
          <template #prefix>
            <n-icon size="20">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
              </svg>
            </n-icon>
          </template>
        </n-input>
        <n-button type="primary" @click="refreshUsers">刷新</n-button>
      </div>

      <n-data-table :columns="columns" :data="filteredUsers" :loading="loading" :pagination="pagination" striped />
      <n-empty v-if="!loading && filteredUsers.length === 0" description="未找到匹配的用户">
        <template #extra>
          <div class="empty-state-actions">
            <n-button @click="searchKeyword = ''">清除搜索</n-button>
            <n-button type="primary" @click="refreshUsers">刷新列表</n-button>
          </div>
          <div class="empty-state-tips">
            <h4>提示：</h4>
            <ul>
              <li>检查搜索关键词是否正确</li>
              <li>可以刷新列表获取最新数据</li>
            </ul>
          </div>
        </template>
      </n-empty>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NPageHeader,
  NInput,
  NButton,
  NIcon,
  NDataTable,
  NTag,
  NSpace
} from 'naive-ui'
import http from '../api/http'

interface User {
  id: number
  email: string
  fullName: string
  phone: string
  campus: string
  role: string
  verified: boolean
  isActive: boolean
  creditScore: number
  createdAt: string
}

const loading = ref(false)
const users = ref<User[]>([])
const searchKeyword = ref('')

// 分页配置
const pagination = {
  pageSize: 10
}

// 角色标签类型映射
const roleTypeMap: Record<string, any> = {
  student: 'info',
  admin: 'error',
  moderator: 'warning'
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API接口获取用户列表
    // 暂时使用模拟数据
    const response = await http.get('/users')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    // 使用模拟数据
    users.value = [
      {
        id: 1,
        email: 'zhangsan@campus.edu',
        fullName: '张三',
        phone: '13800138001',
        campus: '下沙校区',
        role: 'student',
        verified: true,
        isActive: true,
        creditScore: 4.8,
        createdAt: '2025-01-15T10:30:00Z'
      },
      {
        id: 2,
        email: 'lisi@campus.edu',
        fullName: '李四',
        phone: '13800138002',
        campus: '临平校区',
        role: 'student',
        verified: true,
        isActive: true,
        creditScore: 4.2,
        createdAt: '2025-02-20T14:15:00Z'
      },
      {
        id: 3,
        email: 'admin@campus.edu',
        fullName: '管理员',
        phone: '13800138000',
        campus: '下沙校区',
        role: 'admin',
        verified: true,
        isActive: true,
        creditScore: 5.0,
        createdAt: '2022-12-01T09:00:00Z'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 刷新用户列表
const refreshUsers = () => {
  fetchUsers()
}

// 搜索过滤后的用户
const filteredUsers = computed(() => {
  if (!searchKeyword.value) {
    return users.value
  }

  const keyword = searchKeyword.value.toLowerCase()
  return users.value.filter(user =>
    user.fullName.toLowerCase().includes(keyword) ||
    user.email.toLowerCase().includes(keyword) ||
    user.campus.toLowerCase().includes(keyword)
  )
})

// 表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '姓名',
    key: 'fullName',
    width: 120
  },
  {
    title: '邮箱',
    key: 'email',
    ellipsis: true
  },
  {
    title: '校区',
    key: 'campus',
    width: 120
  },
  {
    title: '角色',
    key: 'role',
    width: 100,
    render(row: User) {
      return h(
        NTag,
        { type: roleTypeMap[row.role] || 'default', size: 'small' },
        { default: () => row.role === 'admin' ? '管理员' : row.role === 'student' ? '学生' : row.role }
      )
    }
  },
  {
    title: '信用分',
    key: 'creditScore',
    width: 100,
    render(row: User) {
      return h('span', { style: { color: getCreditScoreColor(row.creditScore) } }, row.creditScore.toFixed(1))
    }
  },
  {
    title: '状态',
    key: 'isActive',
    width: 100,
    render(row: User) {
      return h(
        NTag,
        { type: row.isActive ? 'success' : 'error', size: 'small' },
        { default: () => row.isActive ? '正常' : '禁用' }
      )
    }
  },
  {
    title: '注册时间',
    key: 'createdAt',
    width: 180,
    render(row: User) {
      return new Date(row.createdAt).toLocaleDateString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row: User) {
      return h(
        NSpace,
        {},
        {
          default: () => [
            h(NButton, {
              size: 'small',
              onClick: () => viewUserDetails(row.id)
            }, { default: () => '详情' }),
            h(NButton, {
              size: 'small',
              type: 'primary',
              onClick: () => editUser(row.id)
            }, { default: () => '编辑' })
          ]
        }
      )
    }
  }
]

// 获取信用分颜色
const getCreditScoreColor = (score: number) => {
  if (score >= 4.5) return '#10b981'
  if (score >= 3.5) return '#f59e0b'
  return '#ef4444'
}

// 查看用户详情
const viewUserDetails = (userId: number) => {
  // 跳转到用户详情页面
  console.log('查看用户详情:', userId)
}

// 编辑用户
const editUser = (userId: number) => {
  // 打开编辑用户对话框
  console.log('编辑用户:', userId)
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  padding: 1.5rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 400px;
}

/* 响应式工具栏 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .search-input {
    max-width: 100%;
  }
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