import { useState, useCallback, useRef } from 'react';
import type { InterviewQuestion, RoadmapMode } from '../types';
import { useAuthStore } from '../stores/authStore';

const API_BASE = '/api/v1';

interface UseProgressiveRoadmapOptions {
  onComplete?: (roadmapId: string) => void;
  onError?: (error: string) => void;
}

interface UseProgressiveRoadmapReturn {
  // 상태
  sessionId: string | null;
  questions: InterviewQuestion[];
  answers: Map<string, string>;
  isStreaming: boolean;
  progress: number;
  error: string | null;
  isStarting: boolean;
  isSubmitting: boolean;
  isReadyForGeneration: boolean;

  // 단순화된 2라운드 인터뷰 상태
  currentRound: number;
  maxRounds: number;
  isFollowup: boolean;

  // 액션
  startSession: (params: {
    topic: string;
    mode: RoadmapMode;
    durationMonths: number;
  }) => Promise<void>;
  setAnswer: (questionId: string, answer: string) => void;
  submitRoundAnswers: (userWantsComplete?: boolean) => Promise<void>;
  generateFinalRoadmap: () => Promise<void>;
  reset: () => void;
}

export function useProgressiveRoadmap(
  options: UseProgressiveRoadmapOptions = {}
): UseProgressiveRoadmapReturn {
  const { onComplete, onError } = options;

  // 상태
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [answers, setAnswers] = useState<Map<string, string>>(new Map());
  const [isStreaming, setIsStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isReadyForGeneration, setIsReadyForGeneration] = useState(false);

  // 단순화된 인터뷰 상태
  const [currentRound, setCurrentRound] = useState(1);
  const [maxRounds, setMaxRounds] = useState(2);
  const [isFollowup, setIsFollowup] = useState(false);

  // 참조
  const abortControllerRef = useRef<AbortController | null>(null);
  const token = useAuthStore((state) => state.token);

  // SSE 스트림 읽기 헬퍼
  const readSSEStream = useCallback(
    async (
      response: Response,
      onEvent: (event: { type: string; data?: unknown; progress?: number }) => void
    ) => {
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('응답 스트림을 읽을 수 없습니다');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              onEvent(event);
            } catch (e) {
              console.error('[SSE] 파싱 오류:', e);
            }
          }
        }
      }
    },
    []
  );

  // 세션 시작
  const startSession = useCallback(
    async (params: { topic: string; mode: RoadmapMode; durationMonths: number }) => {
      console.log('[Interview] Starting session with:', params);
      setIsStarting(true);
      setError(null);

      try {
        abortControllerRef.current = new AbortController();

        const response = await fetch(`${API_BASE}/stream/interviews/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            topic: params.topic,
            mode: params.mode,
            duration_months: params.durationMonths,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error('세션 시작 실패');
        }

        await readSSEStream(response, (event) => {
          if (event.progress !== undefined) {
            setProgress(event.progress);
          }

          if (event.type === 'complete' && event.data) {
            const data = event.data as {
              session_id: string;
              questions: InterviewQuestion[];
              current_round?: number;
              max_rounds?: number;
            };
            setSessionId(data.session_id);
            setQuestions(data.questions);
            setCurrentRound(data.current_round || 1);
            setMaxRounds(data.max_rounds || 2);
            console.log('[Interview] Session started with', data.questions.length, 'questions');
          }
        });
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') return;
        const message = err instanceof Error ? err.message : '알 수 없는 오류';
        setError(message);
        onError?.(message);
      } finally {
        setIsStarting(false);
      }
    },
    [token, readSSEStream, onError]
  );

  // 답변 저장 (로컬 상태만)
  const setAnswer = useCallback((questionId: string, answer: string) => {
    setAnswers((prev) => new Map(prev).set(questionId, answer));
  }, []);

  // 라운드별 답변 제출
  const submitRoundAnswers = useCallback(async (userWantsComplete: boolean = false) => {
    if (!sessionId || answers.size === 0) return;

    setIsSubmitting(true);
    setIsStreaming(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      const answersArray = Array.from(answers.entries()).map(([questionId, answer]) => ({
        question_id: questionId,
        answer: answer,
      }));

      const response = await fetch(`${API_BASE}/stream/interviews/${sessionId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          answers: answersArray,
          user_wants_complete: userWantsComplete,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('답변 제출 실패');
      }

      await readSSEStream(response, (event) => {
        if (event.progress !== undefined) {
          setProgress(event.progress);
        }

        if (event.type === 'complete' && event.data) {
          const data = event.data as {
            session_id: string;
            is_complete: boolean;
            current_round?: number;
            max_rounds?: number;
            questions?: InterviewQuestion[];
            is_followup?: boolean;
          };

          if (data.is_complete) {
            // 인터뷰 완료 - 로드맵 생성 준비
            console.log('[Interview] Complete! Ready for roadmap generation');
            setIsReadyForGeneration(true);
          } else {
            // 추가질문 라운드
            console.log('[Interview] Followup questions received:', data.questions?.length);
            setCurrentRound(data.current_round || 2);
            setMaxRounds(data.max_rounds || 2);
            setQuestions(data.questions || []);
            setIsFollowup(data.is_followup || true);
            setAnswers(new Map());  // 새 질문에 대한 답변 초기화
          }
        }
      });
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;
      const message = err instanceof Error ? err.message : '알 수 없는 오류';
      setError(message);
      onError?.(message);
    } finally {
      setIsStreaming(false);
      setIsSubmitting(false);
    }
  }, [sessionId, answers, token, readSSEStream, onError]);

  // 최종 로드맵 생성
  const generateFinalRoadmap = useCallback(async () => {
    if (!sessionId) return;

    setIsStreaming(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      const today = new Date().toISOString().split('T')[0];

      const response = await fetch(`${API_BASE}/stream/roadmaps/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          interview_session_id: sessionId,
          start_date: today,
          use_web_search: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('로드맵 생성 실패');
      }

      await readSSEStream(response, (event) => {
        if (event.progress !== undefined) {
          setProgress(event.progress);
        }

        if (event.type === 'complete' && event.data) {
          const data = event.data as { roadmap_id: string };
          console.log('[Interview] Roadmap generated:', data.roadmap_id);
          onComplete?.(data.roadmap_id);
        }
      });
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;
      const message = err instanceof Error ? err.message : '알 수 없는 오류';
      setError(message);
      onError?.(message);
    } finally {
      setIsStreaming(false);
    }
  }, [sessionId, token, readSSEStream, onComplete, onError]);

  // 리셋
  const reset = useCallback(() => {
    abortControllerRef.current?.abort();
    setSessionId(null);
    setQuestions([]);
    setAnswers(new Map());
    setIsStreaming(false);
    setProgress(0);
    setError(null);
    setIsStarting(false);
    setIsSubmitting(false);
    setIsReadyForGeneration(false);
    setCurrentRound(1);
    setMaxRounds(2);
    setIsFollowup(false);
  }, []);

  return {
    sessionId,
    questions,
    answers,
    isStreaming,
    progress,
    error,
    isStarting,
    isSubmitting,
    isReadyForGeneration,
    currentRound,
    maxRounds,
    isFollowup,
    startSession,
    setAnswer,
    submitRoundAnswers,
    generateFinalRoadmap,
    reset,
  };
}
