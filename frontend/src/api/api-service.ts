/**
 * 统一API服务层
 * 提供统一的API调用接口，简化通信逻辑，提高代码可维护性
 */

import {
  loginRequest,
  registerRequest,
  fetchProfile,
  updateProfile,
  fetchCreditInfo,
} from './auth';

import type {
  LoginRequestPayload,
  RegisterRequestPayload,
  UpdateProfilePayload,
  UserResponse,
  CreditInfoResponse,
  LoginResponse
} from './auth';

import type {
  CreateTaskPayload,
  Task
} from './tasks';

import {
  fetchTasks,
  fetchTaskById,
  createTaskRequest,
  acceptTaskRequest,
  updateTaskStatusRequest,
  cancelTaskRequest,
} from './tasks';



import http from './http';

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  code: number;
  requestId?: string;
}

export interface PaginationParams {
  page?: number;
  size?: number;
  keyword?: string;
  status?: string;
  minReward?: number;
  maxReward?: number;
  pickupLocation?: string;
  dropoffLocation?: string;
  timeRange?: string;
  category?: string;
  urgency?: string;
  sortBy?: string;
  sortOrder?: string;
}

class ApiService {
  // 辅助方法：统一处理API请求
  private async request<T>(apiFunc: () => Promise<T>, successMsg: string, errorMsg: string): Promise<ApiResponse<T>> {
    try {
      const data = await apiFunc();
      return {
        success: true,
        message: successMsg,
        data,
        code: 200
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || errorMsg,
        data: null as any,
        code: error.response?.status || 500
      };
    }
  }

  // 认证相关API
  auth = {
    login: (payload: LoginRequestPayload) => 
      this.request(() => loginRequest(payload), '登录成功', '登录失败'),

    register: (payload: RegisterRequestPayload) => 
      this.request(() => registerRequest(payload), '注册成功', '注册失败'),

    getProfile: () => 
      this.request(() => fetchProfile(), '获取用户信息成功', '获取用户信息失败'),

    updateProfile: (payload: UpdateProfilePayload) => 
      this.request(() => updateProfile(payload), '更新用户信息成功', '更新用户信息失败'),

    getCreditInfo: () => 
      this.request(() => fetchCreditInfo(), '获取信用信息成功', '获取信用信息失败'),
  };

  // 任务相关API
  tasks = {
    list: (params?: Record<string, string | number | undefined>) => 
      this.request(() => fetchTasks(params), '获取任务列表成功', '获取任务列表失败'),

    get: (id: number) => 
      this.request(() => fetchTaskById(id), '获取任务详情成功', '获取任务详情失败'),

    create: (payload: CreateTaskPayload) => 
      this.request(() => createTaskRequest(payload), '创建任务成功', '创建任务失败'),

    accept: (id: number) => 
      this.request(() => acceptTaskRequest(id), '接取任务成功', '接取任务失败'),

    updateStatus: (id: number, status: string) => 
      this.request(() => updateTaskStatusRequest(id, status), '更新任务状态成功', '更新任务状态失败'),

    cancel: (id: number) => 
      this.request(() => cancelTaskRequest(id), '取消任务成功', '取消任务失败'),
  };

  // 通用API方法
  get = async <T>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> => {
    return this.request(async () => {
      const response = await http.get(url, { params });
      return response.data.data;
    }, '请求成功', '请求失败');
  };

  post = async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    return this.request(async () => {
      const response = await http.post(url, data);
      return response.data.data;
    }, '请求成功', '请求失败');
  };

  put = async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    return this.request(async () => {
      const response = await http.put(url, data);
      return response.data.data;
    }, '请求成功', '请求失败');
  };

  delete = async <T>(url: string): Promise<ApiResponse<T>> => {
    return this.request(async () => {
      const response = await http.delete(url);
      return response.data.data;
    }, '请求成功', '请求失败');
  };
}

// 创建API服务实例
export const apiService = new ApiService();

// 导出类型定义
export type { LoginRequestPayload, RegisterRequestPayload, UpdateProfilePayload, UserResponse, CreditInfoResponse, LoginResponse };