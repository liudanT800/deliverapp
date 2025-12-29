import axios, * as AxiosType from 'axios'
import { useAuthStore } from '../stores/auth'

// 定义自定义请求配置接口
interface CustomAxiosRequestConfig extends AxiosType.AxiosRequestConfig {
  _retry?: boolean;
  retryCount?: number;
}

// 请求重试配置
const REQUEST_RETRY_CONFIG = {
  maxRetries: 3,
  baseDelay: 1000, // 初始延迟1秒
  maxDelay: 10000, // 最大延迟10秒
  exponentialBase: 2,
  retryableStatusCodes: [408, 409, 425, 429, 500, 502, 503, 504],
}

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:9800/api',
  timeout: 30_000, // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    const auth = useAuthStore()
    
    // 添加认证头
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    
    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    // 添加时间戳以避免缓存
    if (config.method?.toLowerCase() === 'get') {
      const separator = config.url?.includes('?') ? '&' : '?'
      config.url = `${config.url}${separator}_t=${Date.now()}`
    }
    
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    // 如果响应中有错误信息，则抛出错误
    if (response.data && response.data.success === false) {
      // 即使是 200 OK，如果 success 为 false，也视为业务错误
      // 构造一个类似 AxiosError 的对象，以便后续 catch 块能统一处理
      const error = new Error(response.data.message || '请求失败');
      (error as any).response = response;
      return Promise.reject(error);
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;
    
    // 添加详细的错误日志
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      response: error.response?.data,
    })
    
    // 检查是否为重试请求，避免无限重试
    if (!originalRequest._retry && shouldRetryRequest(error)) {
      originalRequest._retry = true
      
      // 计算重试延迟时间
      const retryCount = originalRequest.retryCount || 0
      if (retryCount < REQUEST_RETRY_CONFIG.maxRetries) {
        const delay = Math.min(
          REQUEST_RETRY_CONFIG.baseDelay * Math.pow(REQUEST_RETRY_CONFIG.exponentialBase, retryCount),
          REQUEST_RETRY_CONFIG.maxDelay
        )
        
        console.log(`请求失败，${delay}ms后重试 (${retryCount + 1}/${REQUEST_RETRY_CONFIG.maxRetries})`)
        
        // 等待指定时间后重试
        await new Promise(resolve => setTimeout(resolve, delay))
        
        // 更新重试计数
        originalRequest.retryCount = retryCount + 1
        
        // 重新发送请求
        return http(originalRequest as AxiosType.AxiosRequestConfig);
      }
    }
    
    // 处理认证错误
    if (error.response?.status === 401) {
      console.log('Authentication failed, logging out user')
      const auth = useAuthStore()
      auth.logout()
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      console.log('Forbidden access - token may be invalid or expired')
      // 可能是令牌无效或已过期，尝试重新登录
      const auth = useAuthStore()
      auth.logout()
      window.location.href = '/login'
    }
    
    // 尝试从响应中提取错误消息
    const message = error.response?.data?.message || error.message || '网络请求失败，请检查网络连接'
    return Promise.reject(new Error(message))
  }
)

// 判断是否应该重试请求
function shouldRetryRequest(error: any): boolean {
  // 网络错误或超时错误
  if (!error.response) {
    return true
  }
  
  // 检查状态码是否在重试列表中
  return REQUEST_RETRY_CONFIG.retryableStatusCodes.includes(error.response.status)
}

export default http