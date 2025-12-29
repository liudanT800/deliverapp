import http from './http'

export interface LoginRequestPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
}

// 后端返回的原始格式
interface BackendTokenResponse {
  access_token: string;
  token_type: string;
}

export function loginRequest(payload: LoginRequestPayload): Promise<LoginResponse> {
  return http
    .post('/auth/login', payload)
    .then((res) => {
      // 将后端返回的下划线格式转换为前端期望的驼峰格式
      const backendData: BackendTokenResponse = res.data.data;
      return {
        accessToken: backendData.access_token,
        tokenType: backendData.token_type,
      };
    })
    .catch((error) => {
      console.error('登录请求失败:', error);
      throw error;
    });
}

export interface RegisterRequestPayload {
  email: string;
  password: string;
  fullName: string;
  campus: string;
  phone: string;
}

export interface UserResponse {
  id: number;
  email: string;
  fullName: string;
  phone: string;
  campus: string;
  creditScore: number;
  createdAt: string;
  updatedAt?: string;
}

export function registerRequest(payload: RegisterRequestPayload): Promise<UserResponse> {
  return http.post('/auth/register', payload)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('注册请求失败:', error);
      throw error;
    });
}

export function fetchProfile(): Promise<UserResponse> {
  return http.get('/users/me')
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('获取用户信息失败:', error);
      throw error;
    });
}

export interface UpdateProfilePayload {
  fullName?: string;
  phone?: string;
  campus?: string;
}

export function updateProfile(payload: UpdateProfilePayload): Promise<UserResponse> {
  return http.put('/users/me', payload)
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('更新用户信息失败:', error);
      throw error;
    });
}

export interface CreditInfoResponse {
  currentScore: number;
  scoreTrend: string;
  completionRates: {
    publish: number;
    take: number;
  };
  taskCounts: {
    published: number;
    taken: number;
  };
  nextLevelRequirements: any;
}

export function fetchCreditInfo(): Promise<CreditInfoResponse> {
  return http.get('/users/me/credit')
    .then((res) => res.data.data)
    .catch((error) => {
      console.error('获取信用信息失败:', error);
      throw error;
    });
}