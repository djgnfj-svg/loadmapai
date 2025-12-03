import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { interviewApi } from '@/lib/api';
import type {
  InterviewQuestion,
  InterviewAnswer,
  InterviewContext,
  InterviewStartResponse,
  InterviewSubmitResponse,
} from '@/types/interview';

interface UseInterviewReturn {
  // State
  sessionId: string | null;
  questions: InterviewQuestion[];
  round: number;
  maxRounds: number;
  interviewContext: InterviewContext | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  startInterview: (topic: string, durationMonths: number) => Promise<void>;
  submitAnswers: (answers: InterviewAnswer[]) => Promise<void>;
  reset: () => void;
}

export function useInterview(): UseInterviewReturn {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [round, setRound] = useState(1);
  const [interviewContext, setInterviewContext] = useState<InterviewContext | null>(null);
  const [error, setError] = useState<string | null>(null);

  const maxRounds = 3;

  const startMutation = useMutation({
    mutationFn: (data: { topic: string; duration_months: number }) =>
      interviewApi.start(data),
    onSuccess: (response) => {
      const data = response.data as InterviewStartResponse;
      setSessionId(data.session_id);
      setQuestions(data.questions);
      setRound(data.round);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message || '인터뷰 시작 중 오류가 발생했습니다.');
    },
  });

  const submitMutation = useMutation({
    mutationFn: (data: { session_id: string; answers: InterviewAnswer[] }) =>
      interviewApi.submit(data),
    onSuccess: (response) => {
      const data = response.data as InterviewSubmitResponse;
      setRound(data.round);

      if (data.status === 'completed') {
        setInterviewContext(data.interview_context || null);
        setQuestions([]);
      } else if (data.status === 'followup_needed' && data.followup_questions) {
        setQuestions(data.followup_questions);
      }
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message || '답변 제출 중 오류가 발생했습니다.');
    },
  });

  const startInterview = useCallback(async (topic: string, durationMonths: number) => {
    await startMutation.mutateAsync({ topic, duration_months: durationMonths });
  }, [startMutation]);

  const submitAnswers = useCallback(async (answers: InterviewAnswer[]) => {
    if (!sessionId) {
      setError('인터뷰 세션이 없습니다.');
      return;
    }
    await submitMutation.mutateAsync({ session_id: sessionId, answers });
  }, [sessionId, submitMutation]);

  const reset = useCallback(() => {
    setSessionId(null);
    setQuestions([]);
    setRound(1);
    setInterviewContext(null);
    setError(null);
  }, []);

  return {
    sessionId,
    questions,
    round,
    maxRounds,
    interviewContext,
    isLoading: startMutation.isPending || submitMutation.isPending,
    error,
    startInterview,
    submitAnswers,
    reset,
  };
}
