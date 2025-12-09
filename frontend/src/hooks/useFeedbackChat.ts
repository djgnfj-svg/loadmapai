/**
 * Feedback chat hook for roadmap refinement
 */
import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { feedbackApi, getErrorMessage } from '@/lib/api';
import type {
  FeedbackMessage,
  RoadmapPreviewData,
  RoadmapModifications,
} from '@/types/feedback';

interface UseFeedbackChatReturn {
  // State
  sessionId: string | null;
  messages: FeedbackMessage[];
  roadmapData: RoadmapPreviewData | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  startSession: (
    roadmapData: RoadmapPreviewData,
    interviewContext?: Record<string, unknown>
  ) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  finalize: () => Promise<{ roadmapId: string; title: string } | null>;
  cancel: () => void;
  reset: () => void;
}

export function useFeedbackChat(): UseFeedbackChatReturn {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<FeedbackMessage[]>([]);
  const [roadmapData, setRoadmapData] = useState<RoadmapPreviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Start session mutation
  const startMutation = useMutation({
    mutationFn: feedbackApi.start,
    onSuccess: (response, variables) => {
      setSessionId(response.data.session_id);
      setRoadmapData(variables.roadmap_data as RoadmapPreviewData);
      // Add welcome message
      setMessages([
        {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: response.data.welcome_message,
          timestamp: new Date(),
        },
      ]);
      setError(null);
    },
    onError: (err: Error) => {
      setError(getErrorMessage(err));
    },
  });

  // Send message mutation
  const messageMutation = useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) =>
      feedbackApi.sendMessage(sessionId, message),
    onSuccess: (response, variables) => {
      const data = response.data;

      // Add user message
      const userMsg: FeedbackMessage = {
        id: `msg-user-${Date.now()}`,
        role: 'user',
        content: variables.message,
        timestamp: new Date(),
      };

      // Add assistant response
      const assistantMsg: FeedbackMessage = {
        id: `msg-assistant-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        modifications: data.modifications as RoadmapModifications | undefined,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);

      // Update roadmap data
      setRoadmapData(data.updated_roadmap as RoadmapPreviewData);
      setError(null);
    },
    onError: (err: Error) => {
      setError(getErrorMessage(err));
    },
  });

  // Finalize mutation
  const finalizeMutation = useMutation({
    mutationFn: (sessionId: string) => feedbackApi.finalize(sessionId),
    onSuccess: () => {
      setError(null);
    },
    onError: (err: Error) => {
      setError(getErrorMessage(err));
    },
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: (sessionId: string) => feedbackApi.cancel(sessionId),
  });

  const startSession = useCallback(
    async (
      roadmapData: RoadmapPreviewData,
      interviewContext?: Record<string, unknown>
    ) => {
      await startMutation.mutateAsync({
        roadmap_data: roadmapData,
        interview_context: interviewContext,
      });
    },
    [startMutation]
  );

  const sendMessage = useCallback(
    async (message: string) => {
      if (!sessionId) {
        setError('세션이 없습니다. 새로 시작해주세요.');
        return;
      }
      await messageMutation.mutateAsync({ sessionId, message });
    },
    [sessionId, messageMutation]
  );

  const finalize = useCallback(async (): Promise<{ roadmapId: string; title: string } | null> => {
    if (!sessionId) {
      setError('세션이 없습니다.');
      return null;
    }
    const result = await finalizeMutation.mutateAsync(sessionId);
    return {
      roadmapId: result.data.roadmap_id,
      title: result.data.title,
    };
  }, [sessionId, finalizeMutation]);

  const cancel = useCallback(() => {
    if (sessionId) {
      cancelMutation.mutate(sessionId);
    }
    reset();
  }, [sessionId, cancelMutation]);

  const reset = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setRoadmapData(null);
    setError(null);
  }, []);

  return {
    sessionId,
    messages,
    roadmapData,
    isLoading:
      startMutation.isPending ||
      messageMutation.isPending ||
      finalizeMutation.isPending,
    error,
    startSession,
    sendMessage,
    finalize,
    cancel,
    reset,
  };
}
