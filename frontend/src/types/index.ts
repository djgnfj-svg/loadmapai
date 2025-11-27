// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
}

// Auth types
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Roadmap types
export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  description: string;
  topic: string;
  duration_months: number;
  start_date: string;
  end_date: string;
  status: 'active' | 'completed' | 'paused';
  created_at: string;
  updated_at: string;
}

export interface MonthlyGoal {
  id: string;
  roadmap_id: string;
  month_number: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface WeeklyTask {
  id: string;
  monthly_goal_id: string;
  week_number: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface DailyTask {
  id: string;
  weekly_task_id: string;
  day_number: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  is_checked: boolean;
}

// Learning types
export interface Question {
  id: string;
  type: 'multiple_choice' | 'short_answer' | 'essay';
  question_text: string;
  options?: string[];
  correct_answer?: string;
}

export interface QuizSession {
  id: string;
  user_id: string;
  daily_task_id: string;
  questions: Question[];
  status: 'in_progress' | 'completed' | 'graded';
  score?: number;
  created_at: string;
}

export interface Answer {
  question_id: string;
  user_answer: string;
  is_correct?: boolean;
  feedback?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
