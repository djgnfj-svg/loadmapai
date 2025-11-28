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
export type RoadmapMode = 'planning' | 'learning';

export type LearningIntensity = 'light' | 'moderate' | 'intense';

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  description: string;
  topic: string;
  duration_months: number;
  start_date: string;
  end_date: string;
  mode: RoadmapMode;
  progress: number;
  status: 'active' | 'completed' | 'paused';
  created_at: string;
  updated_at: string;
  // Schedule fields
  daily_available_minutes?: number;
  rest_days?: number[];
  intensity?: LearningIntensity;
  // Finalization fields
  is_finalized?: boolean;
  finalized_at?: string;
  edit_count_after_finalize?: number;
}

export interface MonthlyGoal {
  id: string;
  roadmap_id: string;
  month_number: number;
  title: string;
  description: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface WeeklyTask {
  id: string;
  monthly_goal_id: string;
  week_number: number;
  title: string;
  description: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface DailyTask {
  id: string;
  weekly_task_id: string;
  day_number: number;
  order: number;  // 같은 day_number 내 순서 (다중 태스크 지원)
  title: string;
  description: string;
  is_checked: boolean;
}

// Full hierarchical types
export interface WeeklyTaskWithDaily extends WeeklyTask {
  daily_tasks: DailyTask[];
}

export interface MonthlyGoalWithWeekly extends MonthlyGoal {
  weekly_tasks: WeeklyTaskWithDaily[];
}

export interface RoadmapFull extends Roadmap {
  monthly_goals: MonthlyGoalWithWeekly[];
}

export interface RoadmapWithMonthly extends Roadmap {
  monthly_goals: MonthlyGoal[];
}

// Learning types
export type QuestionType = 'multiple_choice' | 'short_answer' | 'essay';
export type QuizStatus = 'pending' | 'in_progress' | 'completed' | 'graded';

export interface Question {
  id: string;
  question_number: number;
  question_type: QuestionType;
  question_text: string;
  options?: string[];
  points: number;
  created_at: string;
  // For review (after grading)
  correct_answer?: string;
  explanation?: string;
}

export interface UserAnswer {
  id: string;
  question_id: string;
  answer_text?: string;
  selected_option?: string;
  is_correct?: boolean;
  score?: number;
  feedback?: string;
  created_at: string;
}

export interface Quiz {
  id: string;
  daily_task_id: string;
  status: QuizStatus;
  total_questions: number;
  score?: number;
  correct_count?: number;
  feedback_summary?: string;
  created_at: string;
  updated_at: string;
}

export interface QuizWithQuestions extends Quiz {
  questions: Question[];
}

export interface QuizResult extends Quiz {
  questions: Question[];
  user_answers: UserAnswer[];
}

export interface SubmitAnswerRequest {
  question_id: string;  // 필수: 어느 문제에 대한 답변인지 식별
  answer_text?: string;
  selected_option?: string;
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

// ============ Roadmap Editing Types ============

// CRUD Update types
export interface DailyTaskUpdate {
  title?: string;
  description?: string;
  day_number?: number;
  order?: number;
}

export interface WeeklyTaskUpdate {
  title?: string;
  description?: string;
}

export interface MonthlyGoalUpdate {
  title?: string;
  description?: string;
}

export interface RoadmapScheduleUpdate {
  daily_available_minutes?: number;
  rest_days?: number[];
  intensity?: LearningIntensity;
}

// Chat types
export interface ChatChangeItem {
  id: string;
  target_type: 'roadmap' | 'monthly' | 'weekly' | 'daily';
  target_id?: string;
  action: 'modify' | 'add' | 'delete';
  field?: string;
  old_value?: string;
  new_value?: string;
  parent_id?: string;
}

export interface ChatMessageRequest {
  message: string;
  context?: {
    target_type?: string;
    target_id?: string;
  };
}

export interface ChatMessageResponse {
  message: string;
  changes: ChatChangeItem[];
  suggestions: string[];
}

export interface ApplyChangesRequest {
  change_ids: string[];
  changes: ChatChangeItem[];
}

export interface ApplyChangesResponse {
  success: boolean;
  applied_count: number;
  message: string;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  target_type?: string;
  target_id?: string;
  created_at: string;
}

export interface FinalizeResponse {
  id: string;
  is_finalized: boolean;
  finalized_at?: string;
  message: string;
}
