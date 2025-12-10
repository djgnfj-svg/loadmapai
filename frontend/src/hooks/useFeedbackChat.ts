/**
 * Feedback chat hook for roadmap refinement
 */
import { useState, useCallback, useRef, useMemo } from 'react';
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

  // 세션 시작 중복 방지
  const isStartingRef = useRef(false);

  // Start session mutation
  const startMutation = useMutation({
    mutationFn: feedbackApi.start,
    onSuccess: (response, variables) => {
      setSessionId(response.data.session_id);
      setRoadmapData(variables.roadmap_data as RoadmapPreviewData);
      // Add welcome message
      setMessages([
        {
          id: `msg-welcome-${Date.now()}`,
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

  // Send message mutation (낙관적 업데이트를 위해 onSuccess 제거)
  const messageMutation = useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) =>
      feedbackApi.sendMessage(sessionId, message),
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
      // 이미 시작 중이거나 세션이 있으면 건너뛰기
      if (isStartingRef.current || sessionId) {
        return;
      }

      isStartingRef.current = true;
      try {
        await startMutation.mutateAsync({
          roadmap_data: roadmapData,
          interview_context: interviewContext,
        });
      } finally {
        isStartingRef.current = false;
      }
    },
    [startMutation, sessionId]
  );

  const sendMessage = useCallback(
    async (message: string) => {
      if (!sessionId) {
        setError('세션이 없습니다. 새로 시작해주세요.');
        return;
      }

      // 낙관적 업데이트: 사용자 메시지 즉시 추가
      const optimisticUserMsgId = `msg-user-${Date.now()}`;
      const optimisticUserMsg: FeedbackMessage = {
        id: optimisticUserMsgId,
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, optimisticUserMsg]);
      setError(null);

      try {
        const response = await messageMutation.mutateAsync({ sessionId, message });
        const data = response.data;

        // AI 응답 추가 (사용자 메시지는 이미 추가됨)
        const assistantMsg: FeedbackMessage = {
          id: `msg-assistant-${Date.now()}`,
          role: 'assistant',
          content: data.response,
          modifications: data.modifications as RoadmapModifications | undefined,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMsg]);

        // Update roadmap data
        setRoadmapData(data.updated_roadmap as RoadmapPreviewData);
      } catch (err) {
        // 에러 시 낙관적 메시지 롤백
        setMessages((prev) => prev.filter((m) => m.id !== optimisticUserMsgId));
        setError(getErrorMessage(err as Error));
      }
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, cancelMutation]);

  const reset = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setRoadmapData(null);
    setError(null);
    isStartingRef.current = false;
  }, []);

  const isLoading =
    startMutation.isPending ||
    messageMutation.isPending ||
    finalizeMutation.isPending;

  // useMemo로 반환 객체 메모이제이션
  return useMemo(
    () => ({
      sessionId,
      messages,
      roadmapData,
      isLoading,
      error,
      startSession,
      sendMessage,
      finalize,
      cancel,
      reset,
    }),
    [
      sessionId,
      messages,
      roadmapData,
      isLoading,
      error,
      startSession,
      sendMessage,
      finalize,
      cancel,
      reset,
    ]
  );
}
