import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { loginRequest, registerRequest, fetchProfile, updateProfile, fetchCreditInfo } from '../api/auth'

export interface AuthUser {
  id: number
  email: string
  fullName: string
  role: string
  creditScore: number
  verified: boolean
  campus?: string
  phone?: string
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
  const creditInfo = ref<any>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(payload: LoginPayload) {
    loading.value = true
    try {
      const data = await loginRequest(payload)
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      await getCurrentUser()
      return { success: true }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '登录失败')
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true
    try {
      await registerRequest(payload)
      await login({ email: payload.email, password: payload.password })
      return { success: true, message: '注册成功' }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '注册失败')
    } finally {
      loading.value = false
    }
  }

  async function getCurrentUser() {
    if (!token.value) return
    try {
      const data = await fetchProfile()
      user.value = data
      // 同时获取信用信息
      await loadCreditInfo()
    } catch (error) {
      // 如果获取用户信息失败，清除token
      token.value = null
      localStorage.removeItem('token')
    }
  }

  async function loadCreditInfo() {
    try {
      if (isAuthenticated.value) {
        creditInfo.value = await fetchCreditInfo()
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
      const data = await updateProfile(payload)
      user.value = data
      return { success: true, message: '用户信息更新成功' }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || '更新失败')
    }
  }

  function logout() {
    token.value = null
    user.value = null
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

