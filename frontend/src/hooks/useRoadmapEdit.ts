import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { roadmapApi, chatApi } from '@/lib/api';
import type {
  DailyTaskUpdate,
  WeeklyTaskUpdate,
  MonthlyGoalUpdate,
  RoadmapScheduleUpdate,
  ConversationMessage,
  ChatChangeItem,
} from '@/types';

// ============ Finalization Hooks ============

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

// ============ Schedule Hooks ============

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

// ============ Monthly Goal CRUD Hooks ============

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

// ============ Weekly Task CRUD Hooks ============

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

// ============ Daily Task CRUD Hooks ============

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

// ============ Chat Hooks ============

export function useChatHistory(roadmapId: string, limit = 50) {
  return useQuery({
    queryKey: ['chatHistory', roadmapId],
    queryFn: async () => {
      const response = await chatApi.getHistory(roadmapId, limit);
      return response.data as ConversationMessage[];
    },
    enabled: !!roadmapId,
  });
}

export function useQuickActions(roadmapId: string) {
  return useQuery({
    queryKey: ['quickActions', roadmapId],
    queryFn: async () => {
      const response = await chatApi.getQuickActions(roadmapId);
      return response.data.actions as string[];
    },
    enabled: !!roadmapId,
  });
}

export function useSendChatMessage(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { message: string; context?: { target_type?: string; target_id?: string } }) =>
      chatApi.sendMessage(roadmapId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatHistory', roadmapId] });
    },
  });
}

export function useSendQuickAction(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (actionName: string) =>
      chatApi.sendQuickAction(roadmapId, actionName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatHistory', roadmapId] });
    },
  });
}

export function useApplyChanges(roadmapId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { change_ids: string[]; changes: ChatChangeItem[] }) =>
      chatApi.applyChanges(roadmapId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId, 'full'] });
      queryClient.invalidateQueries({ queryKey: ['chatHistory', roadmapId] });
    },
  });
}
