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
export type RoadmapMode = 'planning';

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
  order: number;
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

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// ============ Roadmap Editing Types ============

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
