import { useState, useCallback, useRef } from 'react';
import type {
  InterviewQuestion,
  ProgressiveRoadmap,
  RoadmapMode,
  RefinementEvent,
  RoadmapItemWithStatus,
} from '../types';
import { createEmptyProgressiveRoadmap } from '../mocks/data/roadmapMockData';
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
  roadmap: ProgressiveRoadmap | null;
  isStreaming: boolean;
  progress: number;
  error: string | null;
  isStarting: boolean;
  submittingQuestionId: string | null;

  // 액션
  startSession: (params: {
    topic: string;
    mode: RoadmapMode;
    durationMonths: number;
  }) => Promise<void>;
  submitAnswer: (questionId: string, answer: string) => Promise<void>;
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
  const [roadmap, setRoadmap] = useState<ProgressiveRoadmap | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [submittingQuestionId, setSubmittingQuestionId] = useState<string | null>(null);

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
      if (!reader) throw new Error('응답 스트림을 읽을 수 없습니다');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              onEvent(event);
            } catch {
              console.error('SSE 파싱 오류:', line);
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
      setIsStarting(true);
      setError(null);

      try {
        // 빈 스켈레톤으로 초기화 (모두 "???")
        const skeleton = createEmptyProgressiveRoadmap(
          params.topic,
          params.mode,
          params.durationMonths
        );
        setRoadmap(skeleton);

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
              skeleton?: ProgressiveRoadmap;
            };
            setSessionId(data.session_id);
            setQuestions(data.questions);
            if (data.skeleton) {
              setRoadmap(data.skeleton);
            }
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

  // 구체화 이벤트 적용
  const applyRefinement = useCallback(
    (prev: ProgressiveRoadmap, event: RefinementEvent): ProgressiveRoadmap => {
      const updated = { ...prev };

      const createConfirmedItem = (value: string): RoadmapItemWithStatus => ({
        content: value,
        status: 'confirmed',
        isNew: true,
      });

      switch (event.type) {
        case 'title':
          updated.title = createConfirmedItem(event.value);
          break;
        case 'description':
          updated.description = createConfirmedItem(event.value);
          break;
        case 'monthly': {
          const monthIdx = updated.monthly_goals.findIndex(
            (m) => m.month_number === event.path.month_number
          );
          if (monthIdx !== -1) {
            updated.monthly_goals = [...updated.monthly_goals];
            updated.monthly_goals[monthIdx] = {
              ...updated.monthly_goals[monthIdx],
              [event.field]: createConfirmedItem(event.value),
            };
          }
          break;
        }
        case 'weekly': {
          const monthIdx = updated.monthly_goals.findIndex(
            (m) => m.month_number === event.path.month_number
          );
          if (monthIdx !== -1) {
            const weekIdx = updated.monthly_goals[monthIdx].weekly_tasks.findIndex(
              (w) => w.week_number === event.path.week_number
            );
            if (weekIdx !== -1) {
              updated.monthly_goals = [...updated.monthly_goals];
              updated.monthly_goals[monthIdx] = {
                ...updated.monthly_goals[monthIdx],
                weekly_tasks: [...updated.monthly_goals[monthIdx].weekly_tasks],
              };
              updated.monthly_goals[monthIdx].weekly_tasks[weekIdx] = {
                ...updated.monthly_goals[monthIdx].weekly_tasks[weekIdx],
                [event.field]: createConfirmedItem(event.value),
              };
            }
          }
          break;
        }
        case 'daily': {
          const monthIdx = updated.monthly_goals.findIndex(
            (m) => m.month_number === event.path.month_number
          );
          if (monthIdx !== -1) {
            const weekIdx = updated.monthly_goals[monthIdx].weekly_tasks.findIndex(
              (w) => w.week_number === event.path.week_number
            );
            if (weekIdx !== -1) {
              const dayIdx = updated.monthly_goals[monthIdx].weekly_tasks[
                weekIdx
              ].daily_tasks.findIndex((d) => d.day_number === event.path.day_number);
              if (dayIdx !== -1) {
                updated.monthly_goals = [...updated.monthly_goals];
                updated.monthly_goals[monthIdx] = {
                  ...updated.monthly_goals[monthIdx],
                  weekly_tasks: [...updated.monthly_goals[monthIdx].weekly_tasks],
                };
                updated.monthly_goals[monthIdx].weekly_tasks[weekIdx] = {
                  ...updated.monthly_goals[monthIdx].weekly_tasks[weekIdx],
                  daily_tasks: [
                    ...updated.monthly_goals[monthIdx].weekly_tasks[weekIdx].daily_tasks,
                  ],
                };
                updated.monthly_goals[monthIdx].weekly_tasks[weekIdx].daily_tasks[dayIdx] = {
                  ...updated.monthly_goals[monthIdx].weekly_tasks[weekIdx].daily_tasks[dayIdx],
                  [event.field]: createConfirmedItem(event.value),
                };
              }
            }
          }
          break;
        }
      }

      return updated;
    },
    []
  );

  // 답변 제출
  const submitAnswer = useCallback(
    async (questionId: string, answer: string) => {
      if (!sessionId) return;

      setSubmittingQuestionId(questionId);
      setIsStreaming(true);
      setError(null);

      // 답변 저장
      setAnswers((prev) => new Map(prev).set(questionId, answer));

      try {
        abortControllerRef.current = new AbortController();

        const response = await fetch(`${API_BASE}/stream/roadmaps/refine`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            session_id: sessionId,
            question_id: questionId,
            answer,
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

          if (event.type === 'refined' && event.data) {
            const refinement = event.data as RefinementEvent;
            setRoadmap((prev) => (prev ? applyRefinement(prev, refinement) : prev));
          }
        });

        // isNew 플래그 리셋 (애니메이션 후)
        setTimeout(() => {
          setRoadmap((prev) => {
            if (!prev) return prev;
            return resetIsNewFlags(prev);
          });
        }, 1000);
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') return;
        const message = err instanceof Error ? err.message : '알 수 없는 오류';
        setError(message);
        onError?.(message);
      } finally {
        setIsStreaming(false);
        setSubmittingQuestionId(null);
      }
    },
    [sessionId, token, readSSEStream, applyRefinement, onError]
  );

  // 최종 로드맵 생성
  const generateFinalRoadmap = useCallback(async () => {
    if (!sessionId) return;

    setIsStreaming(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      const response = await fetch(`${API_BASE}/stream/roadmaps/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          interview_session_id: sessionId,
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
    setRoadmap(null);
    setIsStreaming(false);
    setProgress(0);
    setError(null);
    setIsStarting(false);
    setSubmittingQuestionId(null);
  }, []);

  return {
    sessionId,
    questions,
    answers,
    roadmap,
    isStreaming,
    progress,
    error,
    isStarting,
    submittingQuestionId,
    startSession,
    submitAnswer,
    generateFinalRoadmap,
    reset,
  };
}

// isNew 플래그 리셋 헬퍼
function resetIsNewFlags(roadmap: ProgressiveRoadmap): ProgressiveRoadmap {
  return {
    ...roadmap,
    title: { ...roadmap.title, isNew: false },
    description: { ...roadmap.description, isNew: false },
    monthly_goals: roadmap.monthly_goals.map((month) => ({
      ...month,
      title: { ...month.title, isNew: false },
      description: { ...month.description, isNew: false },
      weekly_tasks: month.weekly_tasks.map((week) => ({
        ...week,
        title: { ...week.title, isNew: false },
        daily_tasks: week.daily_tasks.map((day) => ({
          ...day,
          title: { ...day.title, isNew: false },
          description: { ...day.description, isNew: false },
        })),
      })),
    })),
  };
}
