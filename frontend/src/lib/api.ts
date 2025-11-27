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
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

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
  list: (params?: { page?: number; size?: number }) =>
    api.get('/roadmaps', { params }),

  get: (id: string) => api.get(`/roadmaps/${id}`),

  create: (data: { topic: string; duration_months: number; start_date: string }) =>
    api.post('/roadmaps', data),

  update: (id: string, data: Partial<{ title: string; status: string }>) =>
    api.patch(`/roadmaps/${id}`, data),

  delete: (id: string) => api.delete(`/roadmaps/${id}`),

  // Monthly goals
  getMonthlyGoals: (roadmapId: string) =>
    api.get(`/roadmaps/${roadmapId}/monthly-goals`),

  // Weekly tasks
  getWeeklyTasks: (monthlyGoalId: string) =>
    api.get(`/monthly-goals/${monthlyGoalId}/weekly-tasks`),

  // Daily tasks
  getDailyTasks: (weeklyTaskId: string) =>
    api.get(`/weekly-tasks/${weeklyTaskId}/daily-tasks`),

  toggleDailyTask: (dailyTaskId: string) =>
    api.patch(`/daily-tasks/${dailyTaskId}/toggle`),
};

// Learning API
export const learningApi = {
  generateQuiz: (dailyTaskId: string) =>
    api.post(`/learning/quiz/generate`, { daily_task_id: dailyTaskId }),

  getQuiz: (quizId: string) => api.get(`/learning/quiz/${quizId}`),

  submitAnswers: (quizId: string, answers: { question_id: string; answer: string }[]) =>
    api.post(`/learning/quiz/${quizId}/submit`, { answers }),

  getHistory: (params?: { page?: number; size?: number }) =>
    api.get('/learning/history', { params }),
};

export default api;
