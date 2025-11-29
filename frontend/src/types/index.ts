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

// ============ Deep Interview Types ============

export type InterviewStatus = 'in_progress' | 'completed' | 'abandoned' | 'terminated';
export type InterviewQuestionType = 'text' | 'single_choice' | 'multiple_choice';
export type AnswerEvaluationStatus = 'sufficient' | 'ambiguous' | 'invalid';

export interface InterviewQuestion {
  id: string;
  question: string;
  question_type: InterviewQuestionType;
  options?: string[];
  placeholder?: string;
  // For follow-up questions
  original_question_id?: string;
  context?: string;  // e.g., "이전에 'X'라고 답변하셨는데..."
  is_retry?: boolean;
}

export interface InterviewAnswer {
  question_id: string;
  answer: string;
}

export interface InterviewStageInfo {
  stage: number;
  questions_count: number;
  answers_count: number;
  completed: boolean;
}

export interface InterviewSchedule {
  daily_minutes?: number;
  rest_days?: number[];
  intensity?: LearningIntensity;
}

export interface InterviewSession {
  id: string;
  user_id: string;
  topic: string;
  mode: string;
  duration_months: number;
  current_stage: number;
  current_round: number;
  max_rounds: number;
  status: InterviewStatus;
  stages: InterviewStageInfo[];
  is_complete: boolean;
  is_terminated: boolean;
  termination_reason?: string;
  warning_message?: string;
  created_at: string;
  updated_at: string;
  roadmap_id?: string;
}

export interface InterviewQuestionsResponse {
  session_id: string;
  current_round: number;
  max_rounds: number;
  questions: InterviewQuestion[];
  is_complete: boolean;
  is_followup: boolean;
  is_terminated?: boolean;
  termination_reason?: string;
  warning_message?: string;
  ambiguous_count?: number;
  invalid_count?: number;
}

export interface InterviewCompletedResponse {
  session_id: string;
  is_complete: boolean;
  forced_completion?: boolean;
  compiled_context: string;
  key_insights: string[];
  schedule: InterviewSchedule;
  can_generate_roadmap: boolean;
}

export interface InterviewSessionListResponse {
  sessions: InterviewSession[];
  total: number;
}

// ============ Roadmap Skeleton Types ============

export interface SkeletonWeek {
  week_number: number;
  title: string;
}

export interface SkeletonMonth {
  month_number: number;
  title: string;
  description: string;
  weeks: SkeletonWeek[];
}

export interface RoadmapSkeleton {
  months: SkeletonMonth[];
}

export interface SkeletonGenerateRequest {
  topic: string;
  mode: RoadmapMode;
  duration_months: number;
}

export interface SkeletonGenerateResponse {
  success: boolean;
  skeleton: RoadmapSkeleton;
  topic: string;
  mode: string;
  duration_months: number;
}

// ============ Progressive Roadmap Types ============

export type RoadmapItemStatus = 'undefined' | 'partial' | 'confirmed';

export interface RoadmapItemWithStatus {
  content: string;  // "???" 또는 실제 내용
  status: RoadmapItemStatus;
  isNew?: boolean;  // 방금 업데이트됨 (애니메이션용)
}

export interface ProgressiveDailyTaskItem {
  title: RoadmapItemWithStatus;
  description?: RoadmapItemWithStatus;
}

export interface ProgressiveDailyTask {
  day_number: number;
  tasks: ProgressiveDailyTaskItem[];  // 하루에 여러 Task 가능
  // Legacy support (단일 Task 형식)
  title?: RoadmapItemWithStatus;
  description?: RoadmapItemWithStatus;
}

export interface ProgressiveWeeklyTask {
  week_number: number;
  title: RoadmapItemWithStatus;
  daily_tasks: ProgressiveDailyTask[];
}

export interface ProgressiveMonthlyGoal {
  month_number: number;
  title: RoadmapItemWithStatus;
  description: RoadmapItemWithStatus;
  weekly_tasks: ProgressiveWeeklyTask[];
}

export interface ProgressiveRoadmap {
  title: RoadmapItemWithStatus;
  description: RoadmapItemWithStatus;
  topic: string;
  mode: RoadmapMode;
  duration_months: number;
  monthly_goals: ProgressiveMonthlyGoal[];
}

export interface RefinementEvent {
  type: 'title' | 'description' | 'monthly' | 'weekly' | 'daily';
  path: {
    month_number?: number;
    week_number?: number;
    day_number?: number;
  };
  field: 'title' | 'description';
  value: string;
}

export interface ProgressiveSessionState {
  sessionId: string | null;
  topic: string;
  mode: RoadmapMode;
  durationMonths: number;
  currentQuestions: InterviewQuestion[];
  answeredQuestions: Map<string, string>;
  roadmap: ProgressiveRoadmap | null;
  isStreaming: boolean;
  progress: number;
  error: string | null;
}
