import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';

const API_URL = import.meta.env.VITE_API_URL ?? '';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ error?: { message?: string } }>) => {
    const status = error.response?.status;
    const errorMessage = error.response?.data?.error?.message;

    if (status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }

    // Enhance error with user-friendly message
    const enhancedError = error as AxiosError & { userMessage?: string };
    enhancedError.userMessage = errorMessage || getDefaultErrorMessage(status);

    return Promise.reject(enhancedError);
  }
);

function getDefaultErrorMessage(status?: number): string {
  switch (status) {
    case 400:
      return '잘못된 요청입니다.';
    case 401:
      return '인증이 필요합니다.';
    case 403:
      return '접근 권한이 없습니다.';
    case 404:
      return '요청한 리소스를 찾을 수 없습니다.';
    case 429:
      return '요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.';
    case 500:
      return '서버 오류가 발생했습니다.';
    case 503:
      return '서비스를 일시적으로 사용할 수 없습니다.';
    default:
      return '네트워크 오류가 발생했습니다.';
  }
}

// Helper to extract user-friendly error message
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    return (error as AxiosError & { userMessage?: string }).userMessage ||
           error.response?.data?.error?.message ||
           getDefaultErrorMessage(error.response?.status);
  }
  if (error instanceof Error) {
    return error.message;
  }
  return '알 수 없는 오류가 발생했습니다.';
}

// Auth API
export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  register: (data: { name: string; email: string; password: string }) =>
    api.post('/auth/register', data),

  me: () => api.get('/auth/me'),

  updateProfile: (data: { name?: string; avatar_url?: string }) =>
    api.patch('/auth/me', data),

  refresh: () => api.post('/auth/refresh'),
};

// Roadmap API
export const roadmapApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/roadmaps', { params }),

  get: (id: string) => api.get(`/roadmaps/${id}`),

  getWithMonthly: (id: string) => api.get(`/roadmaps/${id}/monthly`),

  getFull: (id: string) => api.get(`/roadmaps/${id}/full`),

  create: (data: { topic: string; duration_months: number; start_date: string; mode: string }) =>
    api.post('/roadmaps', data),

  generate: (data: { topic: string; duration_months: number; start_date: string; mode: string }) =>
    api.post('/roadmaps/generate', data),

  update: (id: string, data: Partial<{ title: string; status: string }>) =>
    api.patch(`/roadmaps/${id}`, data),

  delete: (id: string) => api.delete(`/roadmaps/${id}`),

  // Monthly goals
  getMonthlyGoals: (roadmapId: string) =>
    api.get(`/roadmaps/${roadmapId}/monthly`),

  // Weekly tasks
  getWeeklyTasks: (monthlyGoalId: string) =>
    api.get(`/monthly-goals/${monthlyGoalId}/weekly-tasks`),

  // Daily tasks
  getDailyTasks: (weeklyTaskId: string) =>
    api.get(`/weekly-tasks/${weeklyTaskId}/daily-tasks`),

  toggleDailyTask: (dailyTaskId: string) =>
    api.patch(`/roadmaps/daily-tasks/${dailyTaskId}/toggle`),

  // ============ Finalization ============
  finalize: (id: string) =>
    api.post(`/roadmaps/${id}/finalize`),

  unfinalize: (id: string) =>
    api.post(`/roadmaps/${id}/unfinalize`),

  // ============ Schedule ============
  updateSchedule: (id: string, data: { daily_available_minutes?: number; rest_days?: number[]; intensity?: string }) =>
    api.patch(`/roadmaps/${id}/schedule`, data),

  // ============ CRUD - Monthly Goals ============
  createMonthlyGoal: (roadmapId: string, data: { month_number: number; title: string; description?: string }) =>
    api.post(`/roadmaps/${roadmapId}/monthly-goals`, data),

  updateMonthlyGoal: (roadmapId: string, goalId: string, data: { title?: string; description?: string }) =>
    api.patch(`/roadmaps/${roadmapId}/monthly-goals/${goalId}`, data),

  deleteMonthlyGoal: (roadmapId: string, goalId: string) =>
    api.delete(`/roadmaps/${roadmapId}/monthly-goals/${goalId}`),

  // ============ CRUD - Weekly Tasks ============
  createWeeklyTask: (goalId: string, data: { week_number: number; title: string; description?: string }) =>
    api.post(`/roadmaps/monthly-goals/${goalId}/weekly-tasks`, data),

  updateWeeklyTask: (goalId: string, taskId: string, data: { title?: string; description?: string }) =>
    api.patch(`/roadmaps/monthly-goals/${goalId}/weekly-tasks/${taskId}`, data),

  deleteWeeklyTask: (goalId: string, taskId: string) =>
    api.delete(`/roadmaps/monthly-goals/${goalId}/weekly-tasks/${taskId}`),

  // ============ CRUD - Daily Tasks ============
  createDailyTask: (weeklyId: string, data: { day_number: number; title: string; description?: string; order?: number }) =>
    api.post(`/roadmaps/weekly-tasks/${weeklyId}/daily-tasks`, data),

  updateDailyTask: (weeklyId: string, taskId: string, data: { title?: string; description?: string; day_number?: number; order?: number }) =>
    api.patch(`/roadmaps/weekly-tasks/${weeklyId}/daily-tasks/${taskId}`, data),

  deleteDailyTask: (weeklyId: string, taskId: string) =>
    api.delete(`/roadmaps/weekly-tasks/${weeklyId}/daily-tasks/${taskId}`),

  reorderDailyTasks: (data: { tasks: { id: string; order: number }[] }) =>
    api.post('/roadmaps/daily-tasks/reorder', data),
};

export default api;
