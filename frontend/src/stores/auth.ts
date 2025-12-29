import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { apiService } from '../api/api-service'

// 从API服务导入类型
import type { LoginRequestPayload, RegisterRequestPayload, CreditInfoResponse, LoginResponse } from '../api/auth'

export interface AuthUser {
  id: number
  email: string
  fullName: string
  role: string
  creditScore: number
  verified: boolean
  campus?: string
  phone?: string
  avatarUrl?: string
}

interface LoginPayload {
  email: string
  password: string
}

interface RegisterPayload extends LoginPayload {
  fullName: string
  campus: string
  phone: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<AuthUser | null>(null)
  const creditInfo = ref<CreditInfoResponse | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(payload: LoginPayload) {
    loading.value = true
    try {
      const response = await apiService.auth.login(payload as LoginRequestPayload)
      if (response.success && response.data) {
        // 从响应中获取token
        // login API返回的是Token对象
        const tokenData = response.data as LoginResponse;
        token.value = tokenData.accessToken;
        localStorage.setItem('token', tokenData.accessToken);
        await getCurrentUser()
        return { success: true }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true
    try {
      const response = await apiService.auth.register(payload as RegisterRequestPayload)
      if (response.success) {
        // 注册成功后自动登录
        await login({ email: payload.email, password: payload.password })
        return { success: true, message: '注册成功' }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    } finally {
      loading.value = false
    }
  }

  async function getCurrentUser() {
    if (!token.value) return
    try {
      const response = await apiService.auth.getProfile()
      if (response.success && response.data) {
        user.value = response.data as unknown as AuthUser
        // 同时获取信用信息
        await loadCreditInfo()
      } else {
        console.error('获取用户信息失败:', response.message)
        // 如果获取用户信息失败，清除token
        token.value = null
        user.value = null
        localStorage.removeItem('token')
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，清除token
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  async function loadCreditInfo() {
    try {
      if (isAuthenticated.value) {
        const response = await apiService.auth.getCreditInfo()
        if (response.success && response.data) {
          creditInfo.value = response.data
        } else {
          console.error('获取信用信息失败:', response.message)
        }
      }
    } catch (error) {
      console.error('获取信用信息失败:', error)
    }
  }

  async function updateUserProfile(payload: {
    fullName?: string
    phone?: string
    campus?: string
    avatarUrl?: string
  }) {
    if (!token.value) return
    try {
      const response = await apiService.auth.updateProfile(payload)
      if (response.success && response.data) {
        user.value = response.data as unknown as AuthUser
        return { success: true, message: '用户信息更新成功' }
      } else {
        throw new Error(response.message || '更新失败')
      }
    } catch (error: any) {
      throw new Error(error.message || '更新失败')
    }
  }

  function logout() {
    token.value = null
    user.value = null
    creditInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    creditInfo,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    getCurrentUser,
    updateUserProfile,
    loadCreditInfo,
  }
})

