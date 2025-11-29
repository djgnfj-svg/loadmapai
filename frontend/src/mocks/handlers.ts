import { http, HttpResponse, delay } from 'msw';
import {
  mockQuestions,
  mockInterviewStartSSE,
  getMockRefinements,
  createMockSSESequence,
  createEmptyProgressiveRoadmap,
} from './data/roadmapMockData';

const API_BASE = '/api/v1';

// SSE 스트림 생성 헬퍼
function createSSEStream(events: Array<{ delay: number; data: unknown }>) {
  const encoder = new TextEncoder();

  return new ReadableStream({
    async start(controller) {
      for (const event of events) {
        await delay(event.delay);
        const sseData = `data: ${JSON.stringify(event.data)}\n\n`;
        controller.enqueue(encoder.encode(sseData));
      }
      controller.close();
    },
  });
}

export const handlers = [
  // ============ 로그인 Mock ============
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as {
      email: string;
      password: string;
    };

    await delay(300);

    // 테스트 계정 허용
    if (body.email && body.password) {
      return HttpResponse.json({
        access_token: 'mock-access-token-' + Date.now(),
        refresh_token: 'mock-refresh-token-' + Date.now(),
        token_type: 'bearer',
        user: {
          id: 1,
          email: body.email,
          nickname: '테스트 사용자',
          created_at: new Date().toISOString(),
        },
      });
    }

    return new HttpResponse(
      JSON.stringify({ detail: '이메일 또는 비밀번호가 올바르지 않습니다.' }),
      { status: 401 }
    );
  }),

  // ============ 현재 사용자 조회 Mock ============
  http.get(`${API_BASE}/auth/me`, async ({ request }) => {
    const authHeader = request.headers.get('Authorization');

    if (authHeader?.startsWith('Bearer ')) {
      return HttpResponse.json({
        id: 1,
        email: 'test@test.com',
        nickname: '테스트 사용자',
        created_at: new Date().toISOString(),
      });
    }

    return new HttpResponse(
      JSON.stringify({ detail: '인증이 필요합니다.' }),
      { status: 401 }
    );
  }),

  // ============ 인터뷰 시작 (SSE) ============
  http.post(`${API_BASE}/stream/interviews/start`, async ({ request }) => {
    const body = (await request.json()) as {
      topic: string;
      mode: string;
      duration_months: number;
    };

    // 스켈레톤 생성
    const skeleton = createEmptyProgressiveRoadmap(
      body.topic,
      body.mode as 'planning' | 'learning',
      body.duration_months
    );

    // SSE 이벤트 시퀀스 생성
    const events = [
      ...mockInterviewStartSSE.slice(0, -1),
      {
        delay: 400,
        data: {
          type: 'complete',
          message: '준비 완료',
          progress: 100,
          data: {
            session_id: 'mock-session-' + Date.now(),
            questions: mockQuestions,
            skeleton,
          },
        },
      },
    ];

    const stream = createSSEStream(events);

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  }),

  // ============ 스켈레톤 생성 (REST) ============
  http.post(`${API_BASE}/stream/roadmaps/skeleton`, async ({ request }) => {
    const body = (await request.json()) as {
      topic: string;
      mode: string;
      duration_months: number;
    };

    await delay(500);

    const skeleton = createEmptyProgressiveRoadmap(
      body.topic,
      body.mode as 'planning' | 'learning',
      body.duration_months
    );

    return HttpResponse.json({
      success: true,
      skeleton,
      topic: body.topic,
      mode: body.mode,
      duration_months: body.duration_months,
    });
  }),

  // ============ 답변 제출 및 구체화 (SSE) ============
  http.post(`${API_BASE}/stream/roadmaps/refine`, async ({ request }) => {
    const body = (await request.json()) as {
      session_id: string;
      question_id: string;
      answer: string;
    };

    // 해당 질문에 대한 구체화 이벤트 가져오기
    const refinements = getMockRefinements(body.question_id, body.answer);
    const events = createMockSSESequence(refinements);

    const stream = createSSEStream(events);

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  }),

  // ============ 현재 질문 조회 (REST) ============
  http.get(`${API_BASE}/interviews/:sessionId/questions`, async () => {
    await delay(300);

    return HttpResponse.json({
      session_id: 'mock-session',
      current_round: 1,
      max_rounds: 1,
      questions: mockQuestions,
      is_complete: false,
      is_followup: false,
    });
  }),

  // ============ 로드맵 최종 생성 (SSE) ============
  http.post(`${API_BASE}/stream/roadmaps/generate`, async () => {
    const events = [
      { delay: 100, data: { type: 'start', message: '로드맵 생성 시작...', progress: 0 } },
      { delay: 500, data: { type: 'analyzing_goals', message: '목표 분석 중...', progress: 20 } },
      {
        delay: 800,
        data: {
          type: 'goals_analyzed',
          message: '목표 분석 완료',
          progress: 30,
          data: { title: '나의 학습 로드맵', description: '체계적인 학습 계획' },
        },
      },
      {
        delay: 600,
        data: {
          type: 'monthly_generated',
          message: '월간 계획 생성됨',
          progress: 50,
        },
      },
      {
        delay: 600,
        data: {
          type: 'weekly_generated',
          message: '주간 계획 생성됨',
          progress: 70,
        },
      },
      {
        delay: 600,
        data: {
          type: 'daily_generated',
          message: '일간 태스크 생성됨',
          progress: 90,
        },
      },
      {
        delay: 400,
        data: {
          type: 'complete',
          message: '로드맵 생성 완료',
          progress: 100,
          data: { roadmap_id: 'mock-roadmap-' + Date.now() },
        },
      },
    ];

    const stream = createSSEStream(events);

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  }),
];
