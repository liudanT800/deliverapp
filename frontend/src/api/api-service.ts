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

import type {
  SendMessagePayload,
  Message,
  ChatSession
} from './chat';

import {
  sendMessage,
  getChatHistory,
  getChatSessions,
} from './chat';

import type {
  SubmitEvaluationPayload,
  Evaluation,
  UserEvaluationStats,
  TaskEvaluationInfo
} from './evaluation';

import {
  submitEvaluation,
  getUserEvaluations,
  getTaskEvaluations,
} from './evaluation';

import type {
  WalletInfo,
  Transaction,
  RechargePayload,
  PaymentPayload,
  SettlementPayload
} from './payment';

import {
  getBalance,
  recharge as rechargeWallet,
  getTransactions,
  payForTask,
  settlePayment,
} from './payment';

import type {
  Appeal,
  CreateAppealPayload
} from './appeal';

import {
  getAppeals,
  createAppeal,
  getAppealDetail,
} from './appeal';



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

    get: (id: number) => {
      console.log('API Service: tasks.get called with id:', id, 'type:', typeof id)
      if (!id || isNaN(id)) {
        console.error('API Service: Invalid task id:', id)
        return Promise.resolve({
          success: false,
          message: '无效的任务ID',
          data: null,
          code: 400
        })
      }
      return this.request(() => fetchTaskById(id), '获取任务详情成功', '获取任务详情失败')
    },

    create: (payload: CreateTaskPayload) =>
      this.request(() => createTaskRequest(payload), '创建任务成功', '创建任务失败'),

    accept: (id: number) =>
      this.request(() => acceptTaskRequest(id), '接取任务成功', '接取任务失败'),

    updateStatus: (id: number, status: string) =>
      this.request(() => updateTaskStatusRequest(id, status), '更新任务状态成功', '更新任务状态失败'),

    cancel: (id: number) =>
      this.request(() => cancelTaskRequest(id), '取消任务成功', '取消任务失败'),
  };

  // Chat API
  chat = {
    send: (payload: SendMessagePayload) => this.request(() => sendMessage(payload), '消息发送成功', '消息发送失败'),
    history: (taskId: number) => this.request(() => getChatHistory(taskId), '获取聊天记录成功', '获取聊天记录失败'),
    sessions: () => this.request(() => getChatSessions(), '获取会话列表成功', '获取会话列表失败'),
  };

  // Evaluation API
  evaluation = {
    submit: (payload: SubmitEvaluationPayload) => this.request(() => submitEvaluation(payload), '评价提交成功', '评价提交失败'),
    user: (userId: number) => this.request(() => getUserEvaluations(userId), '获取用户评价成功', '获取用户评价失败'),
    task: (taskId: number) => this.request(() => getTaskEvaluations(taskId), '获取任务评价成功', '获取任务评价失败'),
  };

  // Payment API
  payment = {
    balance: () => this.request(() => getBalance(), '获取余额成功', '获取余额失败'),
    recharge: (payload: RechargePayload) => this.request(() => rechargeWallet(payload), '充值成功', '充值失败'),
    transactions: () => this.request(() => getTransactions(), '获取交易记录成功', '获取交易记录失败'),
    pay: (payload: PaymentPayload) => this.request(() => payForTask(payload), '支付成功', '支付失败'),
    settle: (payload: SettlementPayload) => this.request(() => settlePayment(payload), '结算成功', '结算失败'),
  };

  // Appeal API
  appeal = {
    list: () => this.request(() => getAppeals(), '获取申诉列表成功', '获取申诉列表失败'),
    create: (payload: CreateAppealPayload) => this.request(() => createAppeal(payload), '申诉创建成功', '申诉创建失败'),
    detail: (appealId: number) => this.request(() => getAppealDetail(appealId), '获取申诉详情成功', '获取申诉详情失败'),
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
export type {
  LoginRequestPayload,
  RegisterRequestPayload,
  UpdateProfilePayload,
  UserResponse,
  CreditInfoResponse,
  LoginResponse,
  SendMessagePayload,
  Message,
  ChatSession,
  SubmitEvaluationPayload,
  Evaluation,
  UserEvaluationStats,
  TaskEvaluationInfo,
  WalletInfo,
  Transaction,
  RechargePayload,
  PaymentPayload,
  SettlementPayload,
  Appeal,
  CreateAppealPayload
};