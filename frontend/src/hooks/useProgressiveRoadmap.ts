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

// 피드백 타입
export interface AIFeedback {
  honest_opinion: string;
  encouragement: string;
  suggestions: string[];
}

// 드래프트 로드맵 타입
export interface DraftRoadmap {
  completion_percentage: number;
  months: Array<{
    month: number;
    title: string;
    overview: string;
  }>;
}

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
  isSubmitting: boolean;
  isReadyForGeneration: boolean;  // 배치 제출 완료 후 true

  // 다중 라운드 인터뷰 상태 (NEW)
  currentRound: number;
  maxRounds: number;
  feedback: AIFeedback | null;
  draftRoadmap: DraftRoadmap | null;
  informationLevel: 'insufficient' | 'minimal' | 'sufficient' | 'complete' | null;
  aiRecommendsComplete: boolean;
  canComplete: boolean;

  // 액션
  startSession: (params: {
    topic: string;
    mode: RoadmapMode;
    durationMonths: number;
  }) => Promise<void>;
  setAnswer: (questionId: string, answer: string) => void;
  submitRoundAnswers: (userWantsComplete?: boolean) => Promise<void>;  // NEW: 라운드별 제출
  submitAllAnswers: () => Promise<void>;  // 레거시: 배치 제출
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isReadyForGeneration, setIsReadyForGeneration] = useState(false);

  // 다중 라운드 인터뷰 상태 (NEW)
  const [currentRound, setCurrentRound] = useState(1);
  const [maxRounds, setMaxRounds] = useState(10);
  const [feedback, setFeedback] = useState<AIFeedback | null>(null);
  const [draftRoadmap, setDraftRoadmap] = useState<DraftRoadmap | null>(null);
  const [informationLevel, setInformationLevel] = useState<'insufficient' | 'minimal' | 'sufficient' | 'complete' | null>(null);
  const [aiRecommendsComplete, setAiRecommendsComplete] = useState(false);
  const [canComplete, setCanComplete] = useState(false);

  // 참조
  const abortControllerRef = useRef<AbortController | null>(null);
  const token = useAuthStore((state) => state.token);

  // SSE 스트림 읽기 헬퍼
  const readSSEStream = useCallback(
    async (
      response: Response,
      onEvent: (event: { type: string; data?: unknown; progress?: number }) => void
    ) => {
      console.log('[SSE] Starting to read stream...');
      const reader = response.body?.getReader();
      if (!reader) {
        console.error('[SSE] No reader available');
        throw new Error('응답 스트림을 읽을 수 없습니다');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('[SSE] Stream done');
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log('[SSE] Received chunk:', chunk);
        buffer += chunk;
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          console.log('[SSE] Processing line:', line);
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              console.log('[SSE] Parsed event:', event);
              onEvent(event);
            } catch (e) {
              console.error('[SSE] 파싱 오류:', line, e);
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
      console.log('[startSession] Starting with params:', params);
      console.log('[startSession] Token available:', !!token, token ? `${token.substring(0, 20)}...` : 'null');
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

        console.log('[startSession] Fetching SSE endpoint...');
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

        console.log('[startSession] Response status:', response.status, response.ok);
        if (!response.ok) {
          throw new Error('세션 시작 실패');
        }

        console.log('[startSession] Starting to read SSE stream...');
        await readSSEStream(response, (event) => {
          console.log('[startSession] Received event:', event.type);
          if (event.progress !== undefined) {
            setProgress(event.progress);
          }

          if (event.type === 'complete' && event.data) {
            console.log('[startSession] Complete event received!');
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
        console.log('[startSession] SSE stream finished');
      } catch (err) {
        console.error('[startSession] Error:', err);
        if (err instanceof Error && err.name === 'AbortError') return;
        const message = err instanceof Error ? err.message : '알 수 없는 오류';
        setError(message);
        onError?.(message);
      } finally {
        console.log('[startSession] Finally block - setting isStarting to false');
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

  // 답변 저장 (로컬 상태만 업데이트)
  const setAnswer = useCallback((questionId: string, answer: string) => {
    setAnswers((prev) => new Map(prev).set(questionId, answer));
  }, []);

  // 라운드별 답변 제출 (NEW: 다중 라운드 인터뷰)
  const submitRoundAnswers = useCallback(async (userWantsComplete: boolean = false) => {
    if (!sessionId || answers.size === 0) return;

    setIsSubmitting(true);
    setIsStreaming(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      // Convert Map to array of answer objects
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
            feedback?: AIFeedback;
            draft_roadmap?: DraftRoadmap;
            information_level?: 'insufficient' | 'minimal' | 'sufficient' | 'complete';
            ai_recommends_complete?: boolean;
            can_complete?: boolean;
            // 완료 시 추가 필드
            compiled_context?: string;
            key_insights?: string[];
            schedule?: object;
          };

          if (data.is_complete) {
            // 인터뷰 완료 - 로드맵 생성 준비
            setIsReadyForGeneration(true);
            setFeedback(data.feedback || null);
          } else {
            // 다음 라운드
            setCurrentRound(data.current_round || currentRound + 1);
            setMaxRounds(data.max_rounds || 10);
            setQuestions(data.questions || []);
            setFeedback(data.feedback || null);
            setDraftRoadmap(data.draft_roadmap || null);
            setInformationLevel(data.information_level || null);
            setAiRecommendsComplete(data.ai_recommends_complete || false);
            setCanComplete(data.can_complete || false);
            // 새 질문에 대한 답변 초기화
            setAnswers(new Map());
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
  }, [sessionId, answers, token, readSSEStream, onError, currentRound]);

  // 모든 답변 일괄 제출 (레거시: 배치 제출)
  const submitAllAnswers = useCallback(async () => {
    if (!sessionId || answers.size === 0) return;

    setIsSubmitting(true);
    setIsStreaming(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      // Convert Map to object
      const answersObj: Record<string, string> = {};
      answers.forEach((value, key) => {
        answersObj[key] = value;
      });

      const response = await fetch(`${API_BASE}/stream/interviews/batch-answers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          session_id: sessionId,
          answers: answersObj,
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

        // Handle refinement events from batch processing
        if (event.data && typeof event.data === 'object' && 'type' in event.data) {
          const eventData = event.data as { type: string; data?: RefinementEvent };
          if (eventData.type === 'refined' && eventData.data) {
            const refinement = eventData.data;
            setRoadmap((prev) => (prev ? applyRefinement(prev, refinement) : prev));
          }
        }
      });

      // 배치 제출 성공 - 로드맵 생성 준비 완료
      setIsReadyForGeneration(true);

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
      setIsSubmitting(false);
    }
  }, [sessionId, answers, token, readSSEStream, applyRefinement, onError]);

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
    setIsSubmitting(false);
    setIsReadyForGeneration(false);
    // 다중 라운드 인터뷰 상태 리셋
    setCurrentRound(1);
    setMaxRounds(10);
    setFeedback(null);
    setDraftRoadmap(null);
    setInformationLevel(null);
    setAiRecommendsComplete(false);
    setCanComplete(false);
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
    isSubmitting,
    isReadyForGeneration,
    // 다중 라운드 인터뷰 상태
    currentRound,
    maxRounds,
    feedback,
    draftRoadmap,
    informationLevel,
    aiRecommendsComplete,
    canComplete,
    // 액션
    startSession,
    setAnswer,
    submitRoundAnswers,
    submitAllAnswers,
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
