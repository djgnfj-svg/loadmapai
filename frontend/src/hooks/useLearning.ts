import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learningApi } from '@/lib/api';
import type {
  Question,
  UserAnswer,
  DailyFeedback,
  WrongQuestion,
  LearningDayInfo,
  LearningWeekInfo,
} from '@/types';

/**
 * Get all questions for a daily task
 */
export function useQuestions(dailyTaskId: string) {
  return useQuery({
    queryKey: ['learning', 'questions', dailyTaskId],
    queryFn: async () => {
      const response = await learningApi.getQuestions(dailyTaskId);
      return response.data as Question[];
    },
    enabled: !!dailyTaskId,
  });
}

/**
 * Submit an answer for a question
 */
export function useSubmitAnswer(dailyTaskId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ questionId, answerText }: { questionId: string; answerText: string }) =>
      learningApi.submitAnswer(questionId, answerText),
    onSuccess: (response) => {
      const answer = response.data as UserAnswer;

      // Update the question's answer in cache
      if (dailyTaskId) {
        queryClient.setQueryData<Question[]>(
          ['learning', 'questions', dailyTaskId],
          (oldQuestions) => {
            if (!oldQuestions) return oldQuestions;
            return oldQuestions.map((q) =>
              q.id === answer.question_id ? { ...q, user_answer: answer } : q
            );
          }
        );
        // Also invalidate day info
        queryClient.invalidateQueries({ queryKey: ['learning', 'day-info', dailyTaskId] });
      }
    },
  });
}

/**
 * Complete a day and get grading results
 */
export function useCompleteDay(dailyTaskId: string, weeklyTaskId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => learningApi.completeDay(dailyTaskId),
    onSuccess: () => {
      // Invalidate questions to get graded answers
      queryClient.invalidateQueries({ queryKey: ['learning', 'questions', dailyTaskId] });
      // Invalidate day info
      queryClient.invalidateQueries({ queryKey: ['learning', 'day-info', dailyTaskId] });
      // Invalidate week info if available
      if (weeklyTaskId) {
        queryClient.invalidateQueries({ queryKey: ['learning', 'week-info', weeklyTaskId] });
        queryClient.invalidateQueries({ queryKey: ['learning', 'wrong-questions', weeklyTaskId] });
      }
      // Invalidate roadmap data
      queryClient.invalidateQueries({ queryKey: ['roadmap'] });
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });
}

/**
 * Get daily feedback for a specific day
 */
export function useDailyFeedback(weeklyTaskId: string, dayNumber: number) {
  return useQuery({
    queryKey: ['learning', 'feedback', weeklyTaskId, dayNumber],
    queryFn: async () => {
      const response = await learningApi.getDailyFeedback(weeklyTaskId, dayNumber);
      return response.data as DailyFeedback | null;
    },
    enabled: !!weeklyTaskId && dayNumber > 0,
  });
}

/**
 * Get all wrong questions for a weekly task
 */
export function useWrongQuestions(weeklyTaskId: string) {
  return useQuery({
    queryKey: ['learning', 'wrong-questions', weeklyTaskId],
    queryFn: async () => {
      const response = await learningApi.getWrongQuestions(weeklyTaskId);
      return response.data as WrongQuestion[];
    },
    enabled: !!weeklyTaskId,
  });
}

/**
 * Generate a review session from wrong questions
 */
export function useGenerateReview(weeklyTaskId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => learningApi.generateReview(weeklyTaskId),
    onSuccess: () => {
      // Invalidate week info to update review_available
      queryClient.invalidateQueries({ queryKey: ['learning', 'week-info', weeklyTaskId] });
      // Invalidate roadmap to show new review task
      queryClient.invalidateQueries({ queryKey: ['roadmap'] });
    },
  });
}

/**
 * Get learning day information
 */
export function useLearningDayInfo(dailyTaskId: string) {
  return useQuery({
    queryKey: ['learning', 'day-info', dailyTaskId],
    queryFn: async () => {
      const response = await learningApi.getDayInfo(dailyTaskId);
      return response.data as LearningDayInfo;
    },
    enabled: !!dailyTaskId,
  });
}

/**
 * Get learning week information
 */
export function useLearningWeekInfo(weeklyTaskId: string) {
  return useQuery({
    queryKey: ['learning', 'week-info', weeklyTaskId],
    queryFn: async () => {
      const response = await learningApi.getWeekInfo(weeklyTaskId);
      return response.data as LearningWeekInfo;
    },
    enabled: !!weeklyTaskId,
  });
}

/**
 * Custom hook for managing the current question index
 */
export function useQuestionNavigation(totalQuestions: number) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const goToNext = () => {
    if (currentIndex < totalQuestions - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const goToIndex = (index: number) => {
    if (index >= 0 && index < totalQuestions) {
      setCurrentIndex(index);
    }
  };

  return {
    currentIndex,
    goToNext,
    goToPrevious,
    goToIndex,
    isFirst: currentIndex === 0,
    isLast: currentIndex === totalQuestions - 1,
  };
}
