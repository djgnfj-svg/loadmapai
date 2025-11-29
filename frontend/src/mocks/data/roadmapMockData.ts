import type {
  ProgressiveRoadmap,
  ProgressiveMonthlyGoal,
  ProgressiveWeeklyTask,
  ProgressiveDailyTask,
  RoadmapItemWithStatus,
  InterviewQuestion,
  RefinementEvent,
} from '../../types';

// ============ Helper Functions ============

export function createUndefinedItem(content = '???'): RoadmapItemWithStatus {
  return { content, status: 'undefined' };
}

export function createConfirmedItem(content: string, isNew = false): RoadmapItemWithStatus {
  return { content, status: 'confirmed', isNew };
}

// ============ Mock Questions ============

export const mockQuestions: InterviewQuestion[] = [
  {
    id: 'q1',
    question: '현재 관련 지식이나 경험이 있으신가요?',
    question_type: 'single_choice',
    options: ['없음 (완전 초보)', '조금 있음', '중급', '고급'],
  },
  {
    id: 'q2',
    question: '하루에 얼마나 시간을 투자할 수 있나요?',
    question_type: 'single_choice',
    options: ['30분 이하', '1시간', '2시간', '3시간 이상'],
  },
  {
    id: 'q3',
    question: '구체적으로 달성하고 싶은 목표가 있나요?',
    question_type: 'text',
    placeholder: '예: 토이 프로젝트 완성, 취업 등',
  },
  {
    id: 'q4',
    question: '선호하는 학습 방식이 있나요?',
    question_type: 'single_choice',
    options: ['동영상 강의', '책/문서', '실습 위주', '혼합'],
  },
];

// ============ Mock Interview SSE Events ============

export const mockInterviewStartSSE = [
  { delay: 100, data: { type: 'start', message: '인터뷰를 시작합니다...', progress: 0 } },
  { delay: 200, data: { type: 'progress', message: '질문 생성 중...', progress: 30 } },
  { delay: 300, data: { type: 'progress', message: '질문 준비 완료', progress: 70 } },
  // complete는 handlers.ts에서 추가
];

// ============ Mock Refinements ============

export function getMockRefinements(questionId: string, answer: string): RefinementEvent[] {
  // 질문별 구체화 로직 (간단한 예시)
  const refinements: RefinementEvent[] = [];

  if (questionId === 'q1') {
    refinements.push({
      type: 'monthly',
      field: 'title',
      value: answer.includes('초보') ? '기초부터 시작' : '핵심 개념 학습',
      path: { month_number: 1 },
    });
  }

  if (questionId === 'q2') {
    refinements.push({
      type: 'description',
      value: `매일 ${answer} 학습 계획`,
      path: {},
    });
  }

  if (questionId === 'q3' && answer.trim()) {
    refinements.push({
      type: 'title',
      value: answer.slice(0, 50) + ' 로드맵',
      path: {},
    });
  }

  return refinements;
}

// ============ SSE Sequence Helper ============

export function createMockSSESequence(refinements: RefinementEvent[]) {
  const events = [
    { delay: 100, data: { type: 'start', message: '답변 분석 중...', progress: 0 } },
  ];

  refinements.forEach((ref, i) => {
    events.push({
      delay: 200,
      data: {
        type: 'progress',
        message: `로드맵 업데이트 중... (${i + 1}/${refinements.length})`,
        progress: 20 + ((i + 1) / refinements.length) * 60,
        data: { type: 'refined', data: ref },
      },
    });
  });

  events.push({
    delay: 100,
    data: { type: 'complete', message: '업데이트 완료', progress: 100 },
  });

  return events;
}

// ============ Initial Skeleton (모두 "???") ============

/**
 * 빈 로드맵 스켈레톤 생성
 * AI가 구체화하기 전 초기 구조를 제공합니다.
 */
export function createEmptyProgressiveRoadmap(
  topic: string,
  mode: 'planning' | 'learning',
  durationMonths: number
): ProgressiveRoadmap {
  const months: ProgressiveMonthlyGoal[] = [];

  for (let m = 1; m <= durationMonths; m++) {
    const weeks: ProgressiveWeeklyTask[] = [];
    for (let w = 1; w <= 4; w++) {
      const days: ProgressiveDailyTask[] = [];
      for (let d = 1; d <= 7; d++) {
        // 새 형식: tasks 배열 사용 (1-3개 Task)
        const taskCount = Math.floor(Math.random() * 3) + 1;
        const tasks = [];
        for (let t = 0; t < taskCount; t++) {
          tasks.push({
            title: createUndefinedItem(),
            description: createUndefinedItem(),
          });
        }
        days.push({
          day_number: d,
          tasks,
        });
      }
      weeks.push({
        week_number: w,
        title: createUndefinedItem(),
        daily_tasks: days,
      });
    }
    months.push({
      month_number: m,
      title: createUndefinedItem(),
      description: createUndefinedItem(),
      weekly_tasks: weeks,
    });
  }

  return {
    title: createUndefinedItem(),
    description: createUndefinedItem(),
    topic,
    mode,
    duration_months: durationMonths,
    monthly_goals: months,
  };
}
