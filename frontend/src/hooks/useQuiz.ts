import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { quizApi } from '@/lib/api';
import type { Quiz, QuizWithQuestions, QuizResult, SubmitAnswerRequest } from '@/types';

export function useQuizzes(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['quizzes', params],
    queryFn: async () => {
      const response = await quizApi.list(params);
      return response.data as Quiz[];
    },
  });
}

export function useQuizForDailyTask(dailyTaskId: string) {
  return useQuery({
    queryKey: ['quiz', 'daily-task', dailyTaskId],
    queryFn: async () => {
      const response = await quizApi.getForDailyTask(dailyTaskId);
      return response.data as Quiz;
    },
    enabled: !!dailyTaskId,
    retry: false,
  });
}

export function useQuiz(quizId: string) {
  return useQuery({
    queryKey: ['quiz', quizId],
    queryFn: async () => {
      const response = await quizApi.get(quizId);
      return response.data as QuizWithQuestions;
    },
    enabled: !!quizId,
  });
}

export function useGenerateQuiz() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ dailyTaskId, numQuestions }: { dailyTaskId: string; numQuestions?: number }) =>
      quizApi.generate(dailyTaskId, numQuestions),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quiz', 'daily-task', variables.dailyTaskId] });
      queryClient.invalidateQueries({ queryKey: ['quizzes'] });
    },
  });
}

export function useStartQuiz() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (quizId: string) => quizApi.start(quizId),
    onSuccess: (_, quizId) => {
      queryClient.invalidateQueries({ queryKey: ['quiz', quizId] });
    },
  });
}

export function useSubmitQuiz() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ quizId, answers }: { quizId: string; answers: SubmitAnswerRequest[] }) =>
      quizApi.submit(quizId, answers),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quiz', variables.quizId] });
    },
  });
}

export function useGradeQuiz() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (quizId: string) => quizApi.grade(quizId),
    onSuccess: (_, quizId) => {
      queryClient.invalidateQueries({ queryKey: ['quiz', quizId] });
      queryClient.invalidateQueries({ queryKey: ['quizzes'] });
    },
  });
}

export function useSubmitAnswer() {
  return useMutation({
    mutationFn: ({ questionId, answer }: { questionId: string; answer: SubmitAnswerRequest }) =>
      quizApi.submitAnswer(questionId, answer),
  });
}
