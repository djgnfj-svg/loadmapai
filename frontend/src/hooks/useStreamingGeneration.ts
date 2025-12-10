/**
 * SSE 스트리밍 로드맵 생성 훅
 *
 * fetch + ReadableStream을 사용하여 SSE 이벤트를 처리합니다.
 * POST 요청을 지원하기 위해 EventSource 대신 fetch를 사용합니다.
 */
import { useState, useCallback, useRef } from 'react';
import { useAuthStore } from '@/stores/authStore';

const API_URL = import.meta.env.VITE_API_URL ?? '';

// SSE 이벤트 타입들
interface TitleReadyData {
  title: string;
  description: string;
}

interface MonthReadyData {
  month_number: number;
  title: string;
  description: string;
}

interface WeeksReadyData {
  month_number: number;
  weeks: Array<{
    week_number: number;
    title: string;
    description: string;
  }>;
}

interface ProgressData {
  current_step: number;
  total_steps: number;
  percentage: number;
  message: string;
}

interface CompleteData {
  roadmap_id: string;
  title: string;
  is_finalized: boolean;
}

interface PreviewReadyData {
  title: string;
  description: string;
  topic: string;
  duration_months: number;
  start_date: string;
  mode: string;
  monthly_goals: Array<{ month_number: number; title: string; description: string }>;
  weekly_tasks: Array<{ month_number: number; weeks: Array<{ week_number: number; title: string; description: string }> }>;
  interview_context?: Record<string, unknown>;
}

interface ErrorData {
  message: string;
  recoverable: boolean;
}

// 프리뷰 월 데이터
export interface MonthPreview {
  month_number: number;
  title: string;
  description: string;
  weeks: Array<{
    week_number: number;
    title: string;
    description: string;
  }>;
}

// 전체 생성 상태
export interface StreamingState {
  status: 'idle' | 'connecting' | 'streaming' | 'complete' | 'preview_ready' | 'error';
  title: string | null;
  description: string | null;
  months: MonthPreview[];
  progress: ProgressData | null;
  roadmapId: string | null;
  previewData: PreviewReadyData | null;  // preview_ready 시 전체 데이터
  error: string | null;
}

// 생성 요청 파라미터
export interface GenerateParams {
  topic: string;
  duration_months: number;
  start_date: string;
  mode: string;
  interview_context?: Record<string, unknown>;
  skip_save?: boolean;  // true면 DB 저장 없이 preview_ready 이벤트 발송
}

const initialState: StreamingState = {
  status: 'idle',
  title: null,
  description: null,
  months: [],
  progress: null,
  roadmapId: null,
  previewData: null,
  error: null,
};

export function useStreamingGeneration() {
  const [state, setState] = useState<StreamingState>(initialState);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { token } = useAuthStore();

  /**
   * SSE 이벤트 핸들러
   */
  const handleEvent = useCallback((eventType: string, data: unknown) => {
    switch (eventType) {
      case 'title_ready': {
        const { title, description } = data as TitleReadyData;
        setState((prev) => ({ ...prev, title, description }));
        break;
      }

      case 'month_ready': {
        const monthData = data as MonthReadyData;
        setState((prev) => ({
          ...prev,
          months: [
            ...prev.months,
            {
              ...monthData,
              weeks: [], // 주간은 아직 비어있음
            },
          ],
        }));
        break;
      }

      case 'weeks_ready': {
        const { month_number, weeks } = data as WeeksReadyData;
        setState((prev) => ({
          ...prev,
          months: prev.months.map((m) =>
            m.month_number === month_number ? { ...m, weeks } : m
          ),
        }));
        break;
      }

      case 'progress': {
        const progressData = data as ProgressData;
        setState((prev) => ({ ...prev, progress: progressData }));
        break;
      }

      case 'warning': {
        // 경고는 무시 (UI에 표시하지 않음)
        break;
      }

      case 'preview_ready': {
        const previewData = data as PreviewReadyData;
        setState((prev) => ({
          ...prev,
          status: 'preview_ready',
          previewData: previewData,
        }));
        break;
      }

      case 'complete': {
        const { roadmap_id } = data as CompleteData;
        setState((prev) => ({
          ...prev,
          status: 'complete',
          roadmapId: roadmap_id,
        }));
        break;
      }

      case 'error': {
        const { message } = data as ErrorData;
        setState((prev) => ({
          ...prev,
          status: 'error',
          error: message,
        }));
        break;
      }
    }
  }, []);

  /**
   * SSE 스트림 파싱
   */
  const parseSSEStream = useCallback(
    async (reader: ReadableStreamDefaultReader<Uint8Array>) => {
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE 이벤트 파싱 (이벤트는 \n\n으로 구분)
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // 마지막 불완전한 이벤트는 버퍼에 유지

        for (const eventStr of events) {
          if (!eventStr.trim()) continue;

          const lines = eventStr.split('\n');
          let eventType = '';
          let eventData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7);
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6);
            }
          }

          if (eventType && eventData) {
            try {
              const parsedData = JSON.parse(eventData);
              handleEvent(eventType, parsedData);
            } catch {
              // SSE 데이터 파싱 실패 시 무시
            }
          }
        }
      }
    },
    [handleEvent]
  );

  /**
   * 로드맵 생성 시작
   */
  const startGeneration = useCallback(
    async (params: GenerateParams) => {
      // 이전 연결 정리
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      setState({
        ...initialState,
        status: 'connecting',
      });

      try {
        const response = await fetch(`${API_URL}/api/v1/roadmaps/generate-stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(params),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorText = await response.text();
          let errorMessage = '로드맵 생성에 실패했습니다.';
          try {
            const errorJson = JSON.parse(errorText);
            errorMessage = errorJson.detail || errorMessage;
          } catch {
            // JSON 파싱 실패 시 기본 메시지 사용
          }
          throw new Error(errorMessage);
        }

        setState((prev) => ({ ...prev, status: 'streaming' }));

        const reader = response.body?.getReader();

        if (!reader) {
          throw new Error('응답 스트림을 읽을 수 없습니다.');
        }

        await parseSSEStream(reader);
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          // 사용자가 취소한 경우
          setState((prev) => ({ ...prev, status: 'idle' }));
        } else {
          setState((prev) => ({
            ...prev,
            status: 'error',
            error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.',
          }));
        }
      }
    },
    [token, parseSSEStream]
  );

  /**
   * 생성 취소
   */
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState((prev) => ({ ...prev, status: 'idle' }));
  }, []);

  /**
   * 상태 초기화
   */
  const reset = useCallback(() => {
    cancel();
    setState(initialState);
  }, [cancel]);

  return {
    ...state,
    startGeneration,
    cancel,
    reset,
    isIdle: state.status === 'idle',
    isConnecting: state.status === 'connecting',
    isStreaming: state.status === 'streaming',
    isPreviewReady: state.status === 'preview_ready',
    isComplete: state.status === 'complete',
    isError: state.status === 'error',
  };
}
