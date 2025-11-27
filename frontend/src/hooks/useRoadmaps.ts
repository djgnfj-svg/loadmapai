import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roadmapApi } from '@/lib/api';
import type { Roadmap, MonthlyGoal, WeeklyTask, DailyTask, RoadmapFull, RoadmapWithMonthly } from '@/types';

export function useRoadmaps(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['roadmaps', params],
    queryFn: async () => {
      const response = await roadmapApi.list(params);
      return response.data as Roadmap[];
    },
  });
}

export function useRoadmap(id: string) {
  return useQuery({
    queryKey: ['roadmap', id],
    queryFn: async () => {
      const response = await roadmapApi.get(id);
      return response.data as Roadmap;
    },
    enabled: !!id,
  });
}

export function useRoadmapWithMonthly(id: string) {
  return useQuery({
    queryKey: ['roadmap', id, 'monthly'],
    queryFn: async () => {
      const response = await roadmapApi.getWithMonthly(id);
      return response.data as RoadmapWithMonthly;
    },
    enabled: !!id,
  });
}

export function useRoadmapFull(id: string) {
  return useQuery({
    queryKey: ['roadmap', id, 'full'],
    queryFn: async () => {
      const response = await roadmapApi.getFull(id);
      return response.data as RoadmapFull;
    },
    enabled: !!id,
  });
}

export function useCreateRoadmap() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: roadmapApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });
}

export function useUpdateRoadmap(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<{ title: string; status: string }>) =>
      roadmapApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', id] });
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });
}

export function useDeleteRoadmap() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: roadmapApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });
}

export function useMonthlyGoals(roadmapId: string) {
  return useQuery({
    queryKey: ['monthlyGoals', roadmapId],
    queryFn: async () => {
      const response = await roadmapApi.getMonthlyGoals(roadmapId);
      return response.data as MonthlyGoal[];
    },
    enabled: !!roadmapId,
  });
}

export function useWeeklyTasks(monthlyGoalId: string) {
  return useQuery({
    queryKey: ['weeklyTasks', monthlyGoalId],
    queryFn: async () => {
      const response = await roadmapApi.getWeeklyTasks(monthlyGoalId);
      return response.data as WeeklyTask[];
    },
    enabled: !!monthlyGoalId,
  });
}

export function useDailyTasks(weeklyTaskId: string) {
  return useQuery({
    queryKey: ['dailyTasks', weeklyTaskId],
    queryFn: async () => {
      const response = await roadmapApi.getDailyTasks(weeklyTaskId);
      return response.data as DailyTask[];
    },
    enabled: !!weeklyTaskId,
  });
}

export function useToggleDailyTask(weeklyTaskId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: roadmapApi.toggleDailyTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      if (weeklyTaskId) {
        queryClient.invalidateQueries({ queryKey: ['dailyTasks', weeklyTaskId] });
      }
    },
  });
}

export function useGenerateRoadmap() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: roadmapApi.generate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });
}
