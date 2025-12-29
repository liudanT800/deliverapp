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
  // 认证相关API
  auth = {
    login: async (payload: LoginRequestPayload): Promise<ApiResponse<LoginResponse>> => {
      try {
        const data = await loginRequest(payload);
        return {
          success: true,
          message: '登录成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '登录失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    register: async (payload: RegisterRequestPayload): Promise<ApiResponse<UserResponse>> => {
      try {
        const data = await registerRequest(payload);
        return {
          success: true,
          message: '注册成功',
          data,
          code: 201
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '注册失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    getProfile: async (): Promise<ApiResponse<UserResponse>> => {
      try {
        const data = await fetchProfile();
        return {
          success: true,
          message: '获取用户信息成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '获取用户信息失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    updateProfile: async (payload: UpdateProfilePayload): Promise<ApiResponse<UserResponse>> => {
      try {
        const data = await updateProfile(payload);
        return {
          success: true,
          message: '更新用户信息成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '更新用户信息失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    getCreditInfo: async (): Promise<ApiResponse<CreditInfoResponse>> => {
      try {
        const data = await fetchCreditInfo();
        return {
          success: true,
          message: '获取信用信息成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '获取信用信息失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    }
  };

  // 任务相关API
  tasks = {
    list: async (params?: Record<string, string | number | undefined>): Promise<ApiResponse<Task[]>> => {
      try {
        const data = await fetchTasks(params);
        return {
          success: true,
          message: '获取任务列表成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '获取任务列表失败',
          data: [],
          code: error.response?.status || 500
        };
      }
    },

    get: async (id: number): Promise<ApiResponse<Task>> => {
      try {
        const data = await fetchTaskById(id);
        return {
          success: true,
          message: '获取任务详情成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '获取任务详情失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    create: async (payload: CreateTaskPayload): Promise<ApiResponse<Task>> => {
      try {
        const data = await createTaskRequest(payload);
        return {
          success: true,
          message: '创建任务成功',
          data,
          code: 201
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '创建任务失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    accept: async (id: number): Promise<ApiResponse<Task>> => {
      try {
        const data = await acceptTaskRequest(id);
        return {
          success: true,
          message: '接取任务成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '接取任务失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    updateStatus: async (id: number, status: string): Promise<ApiResponse<Task>> => {
      try {
        const data = await updateTaskStatusRequest(id, status);
        return {
          success: true,
          message: '更新任务状态成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '更新任务状态失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    },

    cancel: async (id: number): Promise<ApiResponse<Task>> => {
      try {
        const data = await cancelTaskRequest(id);
        return {
          success: true,
          message: '取消任务成功',
          data,
          code: 200
        };
      } catch (error: any) {
        return {
          success: false,
          message: error.message || '取消任务失败',
          data: null as any,
          code: error.response?.status || 500
        };
      }
    }
  };

  // 通用API方法
  get = async <T>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> => {
    try {
      const response = await http.get(url, { params });
      return {
        success: true,
        message: '请求成功',
        data: response.data.data,
        code: response.status
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        data: null as any,
        code: error.response?.status || 500
      };
    }
  };

  post = async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    try {
      const response = await http.post(url, data);
      return {
        success: true,
        message: '请求成功',
        data: response.data.data,
        code: response.status
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        data: null as any,
        code: error.response?.status || 500
      };
    }
  };

  put = async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    try {
      const response = await http.put(url, data);
      return {
        success: true,
        message: '请求成功',
        data: response.data.data,
        code: response.status
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        data: null as any,
        code: error.response?.status || 500
      };
    }
  };

  delete = async <T>(url: string): Promise<ApiResponse<T>> => {
    try {
      const response = await http.delete(url);
      return {
        success: true,
        message: '请求成功',
        data: response.data.data,
        code: response.status
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        data: null as any,
        code: error.response?.status || 500
      };
    }
  };
}

// 创建API服务实例
export const apiService = new ApiService();

// 导出类型定义
export type { LoginRequestPayload, RegisterRequestPayload, UpdateProfilePayload, UserResponse, CreditInfoResponse, LoginResponse };