import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { interviewApi } from '@/lib/api';
import type {
  InterviewSession,
  InterviewQuestionsResponse,
  InterviewCompletedResponse,
  InterviewAnswer,
  InterviewSessionListResponse,
} from '@/types';

export function useInterviewSessions(params?: { skip?: number; limit?: number; status_filter?: string }) {
  return useQuery({
    queryKey: ['interviews', params],
    queryFn: async () => {
      const response = await interviewApi.list(params);
      return response.data as InterviewSessionListResponse;
    },
  });
}

export function useInterviewSession(sessionId: string) {
  return useQuery({
    queryKey: ['interview', sessionId],
    queryFn: async () => {
      const response = await interviewApi.get(sessionId);
      return response.data as InterviewSession;
    },
    enabled: !!sessionId,
  });
}

export function useInterviewQuestions(sessionId: string) {
  return useQuery({
    queryKey: ['interview', sessionId, 'questions'],
    queryFn: async () => {
      const response = await interviewApi.getQuestions(sessionId);
      return response.data as InterviewQuestionsResponse;
    },
    enabled: !!sessionId,
  });
}

export function useStartInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { topic: string; mode: string; duration_months: number }) =>
      interviewApi.start(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
  });
}

export function useSubmitInterviewAnswers(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (answers: InterviewAnswer[]) =>
      interviewApi.submitAnswers(sessionId, answers),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interview', sessionId] });
      queryClient.invalidateQueries({ queryKey: ['interview', sessionId, 'questions'] });
    },
  });
}

export function useAbandonInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => interviewApi.abandon(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
  });
}

export function useDeleteInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => interviewApi.delete(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
  });
}

export function useGenerateRoadmapFromInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { interview_session_id: string; start_date: string; use_web_search?: boolean }) =>
      interviewApi.generateRoadmap(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
  });
}
