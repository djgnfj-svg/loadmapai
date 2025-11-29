import type {
  InterviewQuestion,
  ProgressiveRoadmap,
  ProgressiveMonthlyGoal,
  ProgressiveWeeklyTask,
  ProgressiveDailyTask,
  RoadmapItemWithStatus,
  RefinementEvent,
} from '../../types';

// ============ Helper Functions ============

export function createUndefinedItem(content = '???'): RoadmapItemWithStatus {
  return { content, status: 'undefined' };
}

export function createConfirmedItem(content: string, isNew = false): RoadmapItemWithStatus {
  return { content, status: 'confirmed', isNew };
}

// ============ Initial Skeleton (모두 "???") ============

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
      for (let d = 1; d <= 5; d++) {
        days.push({
          day_number: d,
          title: createUndefinedItem(),
          description: createUndefinedItem(),
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

// ============ Mock Questions ============

export const mockQuestions: InterviewQuestion[] = [
  {
    id: 'q1_experience',
    question: '이 분야에서 현재 어느 정도 경험이 있으신가요?',
    question_type: 'single_choice',
    options: ['완전 초보', '기초 수준', '중급', '고급'],
    placeholder: undefined,
  },
  {
    id: 'q2_daily_time',
    question: '하루에 얼마나 시간을 투자할 수 있나요?',
    question_type: 'text',
    placeholder: '예: 2시간',
  },
  {
    id: 'q3_focus_area',
    question: '특별히 집중하고 싶은 부분이 있나요?',
    question_type: 'text',
    placeholder: '자유롭게 입력해주세요...',
  },
  {
    id: 'q4_goal',
    question: '이 학습을 통해 달성하고 싶은 최종 목표는 무엇인가요?',
    question_type: 'text',
    placeholder: '예: 포트폴리오 프로젝트 완성, 취업 준비 등',
  },
  {
    id: 'q5_preferred_style',
    question: '선호하는 학습 스타일을 선택해주세요.',
    question_type: 'single_choice',
    options: ['이론 중심', '실습 중심', '프로젝트 기반', '균형잡힌 방식'],
  },
];

// ============ Mock Refinements (질문별 구체화 데이터) ============

interface MockRefinementConfig {
  questionId: string;
  events: RefinementEvent[];
}

// 경험 수준에 따른 월간 계획 구체화
export const experienceRefinements: Record<string, RefinementEvent[]> = {
  '완전 초보': [
    { type: 'monthly', path: { month_number: 1 }, field: 'title', value: '기초 개념 학습' },
    { type: 'monthly', path: { month_number: 1 }, field: 'description', value: '기본 문법과 핵심 개념 이해하기' },
    { type: 'monthly', path: { month_number: 2 }, field: 'title', value: '기초 실습' },
    { type: 'monthly', path: { month_number: 2 }, field: 'description', value: '간단한 예제와 연습문제 풀기' },
  ],
  '기초 수준': [
    { type: 'monthly', path: { month_number: 1 }, field: 'title', value: '핵심 개념 복습 및 심화' },
    { type: 'monthly', path: { month_number: 1 }, field: 'description', value: '기초를 다지고 중급 개념 도입' },
    { type: 'monthly', path: { month_number: 2 }, field: 'title', value: '실전 프로젝트 시작' },
    { type: 'monthly', path: { month_number: 2 }, field: 'description', value: '작은 프로젝트를 통한 실습' },
  ],
  '중급': [
    { type: 'monthly', path: { month_number: 1 }, field: 'title', value: '고급 패턴 학습' },
    { type: 'monthly', path: { month_number: 1 }, field: 'description', value: '디자인 패턴과 모범 사례 학습' },
    { type: 'monthly', path: { month_number: 2 }, field: 'title', value: '실무 프로젝트' },
    { type: 'monthly', path: { month_number: 2 }, field: 'description', value: '실무 수준의 프로젝트 진행' },
  ],
  '고급': [
    { type: 'monthly', path: { month_number: 1 }, field: 'title', value: '아키텍처 설계' },
    { type: 'monthly', path: { month_number: 1 }, field: 'description', value: '시스템 아키텍처 설계 및 최적화' },
    { type: 'monthly', path: { month_number: 2 }, field: 'title', value: '전문가 수준 프로젝트' },
    { type: 'monthly', path: { month_number: 2 }, field: 'description', value: '포트폴리오급 프로젝트 완성' },
  ],
};

// 일일 시간에 따른 주간 계획 구체화
export const dailyTimeRefinements: RefinementEvent[] = [
  { type: 'weekly', path: { month_number: 1, week_number: 1 }, field: 'title', value: '환경 설정 및 첫 걸음' },
  { type: 'weekly', path: { month_number: 1, week_number: 2 }, field: 'title', value: '기본 개념 학습' },
  { type: 'weekly', path: { month_number: 1, week_number: 3 }, field: 'title', value: '실습 시작' },
  { type: 'weekly', path: { month_number: 1, week_number: 4 }, field: 'title', value: '첫 번째 마일스톤' },
];

// 집중 영역에 따른 일간 태스크 구체화
export const focusAreaRefinements: RefinementEvent[] = [
  { type: 'daily', path: { month_number: 1, week_number: 1, day_number: 1 }, field: 'title', value: '개발 환경 설정하기' },
  { type: 'daily', path: { month_number: 1, week_number: 1, day_number: 2 }, field: 'title', value: 'Hello World 프로젝트' },
  { type: 'daily', path: { month_number: 1, week_number: 1, day_number: 3 }, field: 'title', value: '기본 문법 익히기' },
  { type: 'daily', path: { month_number: 1, week_number: 1, day_number: 4 }, field: 'title', value: '연습 문제 풀기' },
  { type: 'daily', path: { month_number: 1, week_number: 1, day_number: 5 }, field: 'title', value: '주간 복습 및 정리' },
];

// 목표에 따른 로드맵 제목/설명 구체화
export const goalRefinements: RefinementEvent[] = [
  { type: 'title', path: {}, field: 'title', value: '나만의 학습 로드맵' },
  { type: 'description', path: {}, field: 'description', value: '체계적인 학습을 통해 목표를 달성하는 여정' },
];

// 학습 스타일에 따른 추가 구체화
export const styleRefinements: Record<string, RefinementEvent[]> = {
  '이론 중심': [
    { type: 'weekly', path: { month_number: 1, week_number: 1 }, field: 'title', value: '이론 기초 다지기' },
    { type: 'weekly', path: { month_number: 1, week_number: 2 }, field: 'title', value: '핵심 이론 심화' },
  ],
  '실습 중심': [
    { type: 'weekly', path: { month_number: 1, week_number: 1 }, field: 'title', value: '바로 시작하는 실습' },
    { type: 'weekly', path: { month_number: 1, week_number: 2 }, field: 'title', value: '다양한 예제 만들기' },
  ],
  '프로젝트 기반': [
    { type: 'weekly', path: { month_number: 1, week_number: 1 }, field: 'title', value: '미니 프로젝트 기획' },
    { type: 'weekly', path: { month_number: 1, week_number: 2 }, field: 'title', value: '프로젝트 구현 시작' },
  ],
  '균형잡힌 방식': [
    { type: 'weekly', path: { month_number: 1, week_number: 1 }, field: 'title', value: '이론과 실습 병행' },
    { type: 'weekly', path: { month_number: 1, week_number: 2 }, field: 'title', value: '학습 내용 적용하기' },
  ],
};

// ============ Refinement Mapping ============

export function getMockRefinements(questionId: string, answer: string): RefinementEvent[] {
  switch (questionId) {
    case 'q1_experience':
      return experienceRefinements[answer] || experienceRefinements['완전 초보'];
    case 'q2_daily_time':
      return dailyTimeRefinements;
    case 'q3_focus_area':
      return focusAreaRefinements;
    case 'q4_goal':
      return goalRefinements;
    case 'q5_preferred_style':
      return styleRefinements[answer] || styleRefinements['균형잡힌 방식'];
    default:
      return [];
  }
}

// ============ SSE Event Simulation ============

export interface MockSSEEvent {
  delay: number;
  data: {
    type: string;
    message?: string;
    data?: unknown;
    progress?: number;
  };
}

export function createMockSSESequence(events: RefinementEvent[]): MockSSEEvent[] {
  const sseEvents: MockSSEEvent[] = [
    { delay: 100, data: { type: 'answer_received', message: '답변 수신 완료', progress: 10 } },
    { delay: 300, data: { type: 'refining_roadmap', message: '로드맵 구체화 중...', progress: 20 } },
  ];

  let progress = 30;
  const progressStep = 60 / events.length;

  events.forEach((event, index) => {
    sseEvents.push({
      delay: 200 + index * 150,
      data: {
        type: 'refined',
        message: `${event.type} 구체화됨`,
        data: event,
        progress: Math.min(90, progress + progressStep * (index + 1)),
      },
    });
  });

  sseEvents.push({ delay: 100, data: { type: 'complete', message: '구체화 완료', progress: 100 } });

  return sseEvents;
}

// ============ Interview Start SSE Sequence ============

export const mockInterviewStartSSE: MockSSEEvent[] = [
  { delay: 100, data: { type: 'start', message: '세션 시작...', progress: 0 } },
  { delay: 300, data: { type: 'generating_questions', message: '맞춤형 질문 생성 중...', progress: 30 } },
  { delay: 500, data: { type: 'generating_skeleton', message: '로드맵 구조 생성 중...', progress: 60 } },
  {
    delay: 400,
    data: {
      type: 'complete',
      message: '준비 완료',
      progress: 100,
      data: {
        session_id: 'mock-session-' + Date.now(),
        questions: mockQuestions,
      },
    },
  },
];
