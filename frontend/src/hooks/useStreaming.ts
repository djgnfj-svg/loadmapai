import { useState, useCallback, useRef } from 'react';
import { useAuthStore } from '@/stores/authStore';

export type StreamEventType =
  | 'start'
  | 'progress'
  | 'complete'
  | 'error'
  | 'generating_questions'
  | 'evaluating_answers'
  | 'generating_followup'
  | 'advancing_stage'
  | 'compiling_context'
  | 'web_searching'
  | 'web_search_result'
  | 'analyzing_goals'
  | 'generating_monthly'
  | 'generating_weekly'
  | 'generating_daily'
  | 'validating'
  | 'saving';

export interface StreamEvent {
  type: StreamEventType;
  message: string;
  data?: Record<string, unknown>;
  progress?: number;
}

export interface StreamingState {
  isStreaming: boolean;
  events: StreamEvent[];
  currentEvent: StreamEvent | null;
  progress: number;
  error: string | null;
  result: unknown | null;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useStreaming<T = unknown>() {
  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    events: [],
    currentEvent: null,
    progress: 0,
    error: null,
    result: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const token = useAuthStore((s) => s.token);

  const startStream = useCallback(
    async (
      endpoint: string,
      body: Record<string, unknown>,
      onEvent?: (event: StreamEvent) => void
    ): Promise<T | null> => {
      // Reset state
      setState({
        isStreaming: true,
        events: [],
        currentEvent: null,
        progress: 0,
        error: null,
        result: null,
      });

      // Create abort controller
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(`${API_URL}/api/v1/stream${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(body),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult: T | null = null;

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.slice(6);
              try {
                const event = JSON.parse(jsonStr) as StreamEvent;

                // Update state
                setState((prev) => ({
                  ...prev,
                  events: [...prev.events, event],
                  currentEvent: event,
                  progress: event.progress ?? prev.progress,
                }));

                // Call callback
                onEvent?.(event);

                // Handle completion
                if (event.type === 'complete') {
                  finalResult = event.data as T;
                  setState((prev) => ({
                    ...prev,
                    isStreaming: false,
                    result: event.data,
                  }));
                }

                // Handle error
                if (event.type === 'error') {
                  setState((prev) => ({
                    ...prev,
                    isStreaming: false,
                    error: event.message,
                  }));
                }
              } catch {
                // Ignore parse errors for keepalive
              }
            }
          }
        }

        return finalResult;
      } catch (error) {
        if ((error as Error).name === 'AbortError') {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: '취소됨',
          }));
          return null;
        }

        const errorMessage =
          error instanceof Error ? error.message : '알 수 없는 오류';
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: errorMessage,
        }));
        return null;
      }
    },
    [token]
  );

  const abort = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    setState({
      isStreaming: false,
      events: [],
      currentEvent: null,
      progress: 0,
      error: null,
      result: null,
    });
  }, []);

  return {
    ...state,
    startStream,
    abort,
    reset,
  };
}

// Specialized hooks for specific use cases
export function useInterviewStreaming() {
  const streaming = useStreaming<{
    session_id: string;
    current_stage?: number;
    questions?: unknown[];
    is_complete?: boolean;
    compiled_context?: string;
    key_insights?: string[];
    schedule?: Record<string, unknown>;
  }>();

  const startInterview = useCallback(
    async (data: { topic: string; mode: string; duration_months: number }) => {
      return streaming.startStream('/interviews/start', data);
    },
    [streaming]
  );

  const submitAnswers = useCallback(
    async (
      sessionId: string,
      answers: { question_id: string; answer: string }[]
    ) => {
      return streaming.startStream(`/interviews/${sessionId}/submit`, {
        answers,
      });
    },
    [streaming]
  );

  return {
    ...streaming,
    startInterview,
    submitAnswers,
  };
}

export function useRoadmapStreaming() {
  const streaming = useStreaming<{
    roadmap_id: string;
    title: string;
  }>();

  const generateRoadmap = useCallback(
    async (data: {
      interview_session_id: string;
      start_date: string;
      use_web_search?: boolean;
    }) => {
      return streaming.startStream('/roadmaps/generate', data);
    },
    [streaming]
  );

  return {
    ...streaming,
    generateRoadmap,
  };
}
