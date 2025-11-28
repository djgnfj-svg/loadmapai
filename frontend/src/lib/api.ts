import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  refresh: () => api.post('/auth/refresh'),

  googleLogin: () => `${API_URL}/api/v1/auth/google`,

  githubLogin: () => `${API_URL}/api/v1/auth/github`,
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
};

// Quiz API
export const quizApi = {
  // List user's quizzes
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/quizzes', { params }),

  // Get quiz for a daily task
  getForDailyTask: (dailyTaskId: string) =>
    api.get(`/quizzes/daily-task/${dailyTaskId}`),

  // Generate new quiz for a daily task
  generate: (dailyTaskId: string, numQuestions: number = 5) =>
    api.post(`/quizzes/daily-task/${dailyTaskId}/generate`, null, {
      params: { num_questions: numQuestions }
    }),

  // Get quiz with questions
  get: (quizId: string) => api.get(`/quizzes/${quizId}`),

  // Start quiz
  start: (quizId: string) => api.post(`/quizzes/${quizId}/start`),

  // Submit all answers
  submit: (quizId: string, answers: { question_id: string; answer_text?: string; selected_option?: string }[]) =>
    api.post(`/quizzes/${quizId}/submit`, { answers }),

  // Grade quiz
  grade: (quizId: string) => api.post(`/quizzes/${quizId}/grade`),

  // Reset quiz (다시 풀기)
  reset: (quizId: string) => api.post(`/quizzes/${quizId}/reset`),

  // Submit single answer
  submitAnswer: (questionId: string, answer: { question_id: string; answer_text?: string; selected_option?: string }) =>
    api.post(`/quizzes/questions/${questionId}/answer`, answer),
};

export default api;
