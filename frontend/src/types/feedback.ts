/**
 * Feedback chat types for roadmap refinement
 */

export interface MonthlyGoalData {
  month_number: number;
  title: string;
  description: string;
}

export interface WeeklyTaskData {
  month_number: number;
  week_number: number;
  title: string;
  description: string;
}

export interface WeeklyTasksGroup {
  month_number: number;
  weeks: Array<{
    week_number: number;
    title: string;
    description: string;
  }>;
}

export interface RoadmapPreviewData {
  topic: string;
  duration_months: number;
  start_date: string;
  mode: string;
  title: string;
  description: string;
  monthly_goals: MonthlyGoalData[];
  weekly_tasks: WeeklyTasksGroup[];
  interview_context?: Record<string, unknown>;
}

export interface RoadmapModifications {
  monthly_goals?: MonthlyGoalData[];
  weekly_tasks?: WeeklyTaskData[];
}

export interface FeedbackMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  modifications?: RoadmapModifications;
  timestamp: Date;
}

// API Request/Response types
export interface FeedbackStartRequest {
  roadmap_data: RoadmapPreviewData;
  interview_context?: Record<string, unknown>;
}

export interface FeedbackStartResponse {
  session_id: string;
  welcome_message: string;
}

export interface FeedbackMessageRequest {
  message: string;
}

export interface FeedbackMessageResponse {
  response: string;
  modifications?: RoadmapModifications;
  updated_roadmap: RoadmapPreviewData;
}

export interface FeedbackFinalizeResponse {
  roadmap_id: string;
  title: string;
}
