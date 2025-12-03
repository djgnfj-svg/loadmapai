import { useMutation, useQueryClient } from '@tanstack/react-query';
import { roadmapApi } from '@/lib/api';
import type {
  DailyTaskUpdate,
  WeeklyTaskUpdate,
  MonthlyGoalUpdate,
  RoadmapScheduleUpdate,
} from '@/types';

export function useFinalizeRoadmap(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => roadmapApi.finalize(roadmapId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId] });
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useUnfinalizeRoadmap(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => roadmapApi.unfinalize(roadmapId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId] });
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useUpdateSchedule(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RoadmapScheduleUpdate) =>
      roadmapApi.updateSchedule(roadmapId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId] });
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useCreateMonthlyGoal(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { month_number: number; title: string; description?: string }) =>
      roadmapApi.createMonthlyGoal(roadmapId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
      queryClient.invalidateQueries({ queryKey: ['monthlyGoals', roadmapId] });
    },
  });
}

export function useUpdateMonthlyGoal(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, data }: { goalId: string; data: MonthlyGoalUpdate }) =>
      roadmapApi.updateMonthlyGoal(roadmapId, goalId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
      queryClient.invalidateQueries({ queryKey: ['monthlyGoals', roadmapId] });
    },
  });
}

export function useDeleteMonthlyGoal(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (goalId: string) =>
      roadmapApi.deleteMonthlyGoal(roadmapId, goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
      queryClient.invalidateQueries({ queryKey: ['monthlyGoals', roadmapId] });
    },
  });
}

export function useCreateWeeklyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, data }: { goalId: string; data: { week_number: number; title: string; description?: string } }) =>
      roadmapApi.createWeeklyTask(goalId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useUpdateWeeklyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, taskId, data }: { goalId: string; taskId: string; data: WeeklyTaskUpdate }) =>
      roadmapApi.updateWeeklyTask(goalId, taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useDeleteWeeklyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, taskId }: { goalId: string; taskId: string }) =>
      roadmapApi.deleteWeeklyTask(goalId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useCreateDailyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ weeklyId, data }: { weeklyId: string; data: { day_number: number; title: string; description?: string; order?: number } }) =>
      roadmapApi.createDailyTask(weeklyId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useUpdateDailyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ weeklyId, taskId, data }: { weeklyId: string; taskId: string; data: DailyTaskUpdate }) =>
      roadmapApi.updateDailyTask(weeklyId, taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useDeleteDailyTask(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ weeklyId, taskId }: { weeklyId: string; taskId: string }) =>
      roadmapApi.deleteDailyTask(weeklyId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}

export function useReorderDailyTasks(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tasks: { id: string; order: number }[]) =>
      roadmapApi.reorderDailyTasks({ tasks }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
    },
  });
}
