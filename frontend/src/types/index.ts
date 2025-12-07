export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export type RoadmapMode = 'PLANNING' | 'LEARNING';

export type LearningIntensity = 'light' | 'moderate' | 'intense';

// Learning Mode Types
export type QuestionType = 'ESSAY' | 'MULTIPLE_CHOICE' | 'SHORT_ANSWER';

export interface UserAnswer {
  id: string;
  question_id: string;
  answer_text: string;
  is_correct?: boolean;
  score?: number;
  feedback?: string;
  submitted_at?: string;
  graded_at?: string;
}

export interface Question {
  id: string;
  daily_task_id: string;
  question_type: QuestionType;
  question_text: string;
  choices?: string[];
  hint?: string;
  order: number;
  user_answer?: UserAnswer;
}

export interface QuestionWithAnswer extends Question {
  correct_answer: string;
  explanation?: string;
}

export interface QuestionResult {
  question_id: string;
  question_type: QuestionType;
  question_text: string;
  your_answer: string;
  correct_answer: string;
  is_correct: boolean;
  score?: number;
  feedback: string;
  explanation?: string;
}

export interface DailyFeedback {
  id: string;
  weekly_task_id: string;
  day_number: number;
  total_questions: number;
  correct_count: number;
  accuracy_rate: number;
  is_passed: boolean;
  summary: string;
  strengths?: string[];
  improvements?: string[];
  question_results?: QuestionResult[];
  created_at: string;
}

export interface CompleteDayResponse {
  feedback: DailyFeedback;
  next_day_available: boolean;
  week_completed: boolean;
}

export interface WrongQuestion {
  question: QuestionWithAnswer;
  your_answer: string;
  day_number: number;
}

export interface ReviewSession {
  daily_task_id: string;
  total_questions: number;
  questions: Question[];
}

export interface LearningDayInfo {
  daily_task_id: string;
  weekly_task_id: string;
  day_number: number;
  title: string;
  description?: string;
  total_questions: number;
  answered_count: number;
  is_completed: boolean;
  feedback?: DailyFeedback;
}

export interface LearningWeekInfo {
  weekly_task_id: string;
  week_number: number;
  title: string;
  description?: string;
  days: LearningDayInfo[];
  total_questions: number;
  correct_count: number;
  accuracy_rate: number;
  is_completed: boolean;
  review_available: boolean;
}

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
  daily_available_minutes?: number;
  rest_days?: number[];
  intensity?: LearningIntensity;
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

export interface DailyGoal {
  id: string;
  weekly_task_id: string;
  day_number: number;
  title: string;
  description: string;
  created_at: string;
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
  daily_goals: DailyGoal[];
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

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

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

export interface FinalizeResponse {
  id: string;
  is_finalized: boolean;
  finalized_at?: string;
  message: string;
}

// Unified View Types
export interface TodayDailyTask {
  id: string;
  title: string;
  description: string | null;
  day_number: number;
  order: number;
  is_checked: boolean;
  actual_date: string;

  // Roadmap context
  roadmap_id: string;
  roadmap_title: string;
  roadmap_topic: string;

  // Weekly task context
  weekly_task_id: string;
  weekly_task_title: string;

  // Monthly goal context
  monthly_goal_id: string;
  monthly_goal_title: string;
}

export interface WeeklyTaskSummary {
  id: string;
  title: string;
  description: string | null;
  week_number: number;
  progress: number;

  // Roadmap context
  roadmap_id: string;
  roadmap_title: string;
  roadmap_topic: string;

  // Monthly goal context
  monthly_goal_id: string;
  monthly_goal_title: string;

  // Daily tasks
  daily_tasks: TodayDailyTask[];

  // Date range
  week_start: string;
  week_end: string;
}

export interface UnifiedViewResponse {
  target_date: string;
  today_tasks: TodayDailyTask[];
  current_week: WeeklyTaskSummary[];

  // Statistics
  today_total: number;
  today_completed: number;
  week_total: number;
  week_completed: number;
}
