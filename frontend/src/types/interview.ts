/**
 * Interview types for SMART-based goal setting
 */

export type InterviewCategory = 'specific' | 'measurable' | 'achievable' | 'relevant';
export type InterviewQuestionType = 'text' | 'select' | 'multiselect';

export interface InterviewQuestion {
  id: string;
  category: InterviewCategory;
  question: string;
  type: InterviewQuestionType;
  options?: string[];
}

export interface InterviewAnswer {
  question_id: string;
  answer: string | string[];
}

export interface InterviewContext {
  specific_goal: string;
  expected_outcome: string;
  measurement_criteria: string;
  current_level: string;
  available_resources: {
    daily_hours?: number;
    tools?: string[];
    prior_knowledge?: string[];
  };
  motivation: string;
  challenges: string[];
}

// API Request/Response types
export interface InterviewStartRequest {
  topic: string;
  duration_months: number;
}

export interface InterviewStartResponse {
  session_id: string;
  questions: InterviewQuestion[];
  round: number;
}

export interface InterviewSubmitRequest {
  session_id: string;
  answers: InterviewAnswer[];
}

export interface InterviewSubmitResponse {
  status: 'completed' | 'followup_needed';
  round: number;
  followup_questions?: InterviewQuestion[];
  interview_context?: InterviewContext;
}

// Category metadata
export const CATEGORY_META: Record<InterviewCategory, { label: string; color: string; bgColor: string }> = {
  specific: {
    label: '구체적 목표',
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-500/20',
  },
  measurable: {
    label: '측정 가능',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-500/20',
  },
  achievable: {
    label: '달성 가능',
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-500/20',
  },
  relevant: {
    label: '관련성',
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-500/20',
  },
};
