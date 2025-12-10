import { http, HttpResponse, delay } from 'msw';

// VITE_API_URL 환경변수 또는 상대 경로 사용
const VITE_API_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = `${VITE_API_URL}/api/v1`;

// ============ Mock 데이터 저장소 ============
const mockFeedbackSessions = new Map<
  string,
  {
    roadmapData: Record<string, unknown>;
    messages: Array<{ role: string; content: string }>;
  }
>();

const mockInterviewSessions = new Map<
  string,
  { round: number; topic: string; duration_months: number }
>();

// ============ 샘플 로드맵 데이터 생성 함수 ============
function generateMockRoadmapData(
  topic: string,
  durationMonths: number,
  startDate: string,
  mode: string
) {
  const monthlyGoals = [];
  const weeklyTasks = [];

  for (let m = 1; m <= durationMonths; m++) {
    monthlyGoals.push({
      month_number: m,
      title: `${m}월차: ${topic} ${m === 1 ? '기초' : m === 2 ? '심화' : '실전'}`,
      description: `${m}월차에는 ${topic}의 ${m === 1 ? '기본 개념을 학습' : m === 2 ? '심화 내용을 학습' : '실전 프로젝트를 진행'}합니다.`,
    });

    const weeks = [];
    for (let w = 1; w <= 4; w++) {
      weeks.push({
        week_number: w,
        title: `${w}주차: ${m === 1 ? '기초 ' : m === 2 ? '심화 ' : '실전 '}과제 ${w}`,
        description: `${m}월차 ${w}주차에 진행할 학습 내용입니다. 핵심 개념을 이해하고 실습해봅니다.`,
      });
    }
    weeklyTasks.push({ month_number: m, weeks });
  }

  return {
    topic,
    duration_months: durationMonths,
    start_date: startDate,
    mode,
    title: `${topic} 마스터하기`,
    description: `${durationMonths}개월 동안 체계적으로 ${topic}을(를) 학습하여 전문가가 되어봅시다.`,
    monthly_goals: monthlyGoals,
    weekly_tasks: weeklyTasks,
  };
}

export const handlers = [
  // ============ 로그인 Mock ============
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as {
      email: string;
      password: string;
    };

    await delay(300);

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

  // ============ 로드맵 목록 조회 ============
  http.get(`${API_BASE}/roadmaps`, async () => {
    await delay(300);
    return HttpResponse.json([
      {
        id: 1,
        title: 'React 마스터하기',
        topic: 'React',
        duration_months: 3,
        start_date: '2025-01-01',
        progress: 25,
        created_at: '2025-01-01T00:00:00Z',
      },
      {
        id: 2,
        title: 'TypeScript 완벽 가이드',
        topic: 'TypeScript',
        duration_months: 2,
        start_date: '2025-02-01',
        progress: 50,
        created_at: '2025-02-01T00:00:00Z',
      },
    ]);
  }),

  // ============ 오늘의 태스크 조회 ============
  http.get(`${API_BASE}/roadmaps/unified/today`, async () => {
    await delay(300);
    return HttpResponse.json({
      tasks: [
        {
          id: 1,
          roadmap_id: 1,
          roadmap_title: 'React 마스터하기',
          title: 'React Hooks 기초 학습',
          description: 'useState, useEffect 훅의 기본 사용법을 익힙니다.',
          is_completed: false,
        },
        {
          id: 2,
          roadmap_id: 2,
          roadmap_title: 'TypeScript 완벽 가이드',
          title: '타입 시스템 이해하기',
          description: 'TypeScript의 기본 타입과 인터페이스를 학습합니다.',
          is_completed: true,
        },
      ],
      total_count: 2,
      completed_count: 1,
    });
  }),

  // ============ 로드맵 생성 가능 여부 확인 ============
  http.get(`${API_BASE}/roadmaps/generate/can-generate`, async () => {
    await delay(200);
    return HttpResponse.json({
      can_generate: true,
      today_count: 0,
      limit: 5,
      reason: null,
    });
  }),

  // ============ 로드맵 생성 (REST) ============
  http.post(`${API_BASE}/roadmaps/generate`, async () => {
    await delay(2000);

    return HttpResponse.json({
      roadmap_id: 'mock-roadmap-' + Date.now(),
      title: '나의 학습 로드맵',
      message: '로드맵이 성공적으로 생성되었습니다.',
    });
  }),

  // ============ 스트리밍 로드맵 생성 (SSE) ============
  http.post(`${API_BASE}/roadmaps/generate-stream`, async ({ request }) => {
    const body = (await request.json()) as {
      topic: string;
      duration_months: number;
      start_date: string;
      mode: string;
      skip_save?: boolean;
      interview_context?: Record<string, unknown>;
    };

    const encoder = new TextEncoder();
    const roadmapData = generateMockRoadmapData(
      body.topic,
      body.duration_months,
      body.start_date,
      body.mode
    );

    const stream = new ReadableStream({
      async start(controller) {
        const sendEvent = (event: string, data: unknown) => {
          controller.enqueue(
            encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)
          );
        };

        // 진행률
        sendEvent('progress', {
          current_step: 1,
          total_steps: 4,
          percentage: 10,
          message: '목표 분석 중...',
        });
        await new Promise((r) => setTimeout(r, 500));

        // 제목 생성
        sendEvent('title_ready', {
          title: roadmapData.title,
          description: roadmapData.description,
        });
        await new Promise((r) => setTimeout(r, 300));

        // 월별 목표 생성
        for (let m = 0; m < roadmapData.monthly_goals.length; m++) {
          sendEvent('progress', {
            current_step: 2,
            total_steps: 4,
            percentage: 20 + ((m + 1) / roadmapData.monthly_goals.length) * 30,
            message: `${m + 1}월차 계획 생성 중...`,
          });
          sendEvent('month_ready', roadmapData.monthly_goals[m]);
          await new Promise((r) => setTimeout(r, 400));
        }

        // 주간 과제 생성
        for (let m = 0; m < roadmapData.weekly_tasks.length; m++) {
          sendEvent('progress', {
            current_step: 3,
            total_steps: 4,
            percentage: 50 + ((m + 1) / roadmapData.weekly_tasks.length) * 40,
            message: `${m + 1}월차 주간 과제 생성 중...`,
          });
          sendEvent('weeks_ready', roadmapData.weekly_tasks[m]);
          await new Promise((r) => setTimeout(r, 300));
        }

        // skip_save가 true면 preview_ready, 아니면 complete
        if (body.skip_save) {
          sendEvent('preview_ready', {
            ...roadmapData,
            interview_context: body.interview_context,
          });
        } else {
          sendEvent('complete', {
            roadmap_id: 'mock-roadmap-' + Date.now(),
            title: roadmapData.title,
            is_finalized: false,
          });
        }

        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  }),

  // ============ 인터뷰 시작 ============
  http.post(`${API_BASE}/interview/start`, async ({ request }) => {
    const body = (await request.json()) as {
      topic: string;
      duration_months: number;
    };

    await delay(800);

    const sessionId = `mock-interview-session-${Date.now()}`;
    mockInterviewSessions.set(sessionId, {
      round: 1,
      topic: body.topic,
      duration_months: body.duration_months,
    });

    return HttpResponse.json({
      session_id: sessionId,
      round: 1,
      questions: [
        {
          id: 'q1',
          category: 'specific',
          type: 'select',
          question: '현재 이 분야에 대한 경험이 어느 정도인가요?',
          options: ['완전 초보자', '기초 지식 있음', '중급자', '고급자'],
        },
        {
          id: 'q2',
          category: 'achievable',
          type: 'select',
          question: '하루에 학습에 투자할 수 있는 시간은?',
          options: ['30분 미만', '30분~1시간', '1~2시간', '2시간 이상'],
        },
        {
          id: 'q3',
          category: 'relevant',
          type: 'text',
          question: '이 목표를 달성하려는 특별한 이유가 있나요?',
        },
        {
          id: 'q4',
          category: 'measurable',
          type: 'select',
          question: '어떤 결과를 달성하면 성공이라고 할 수 있나요?',
          options: ['기초 개념 이해', '간단한 프로젝트 완성', '실무 수준 역량', '전문가 수준'],
        },
      ],
    });
  }),

  // ============ 인터뷰 답변 제출 ============
  http.post(`${API_BASE}/interview/submit`, async ({ request }) => {
    const body = (await request.json()) as {
      session_id: string;
      answers: Array<{ question_id: string; answer: string | string[] }>;
    };

    await delay(1000);

    const session = mockInterviewSessions.get(body.session_id);
    if (!session) {
      return new HttpResponse(
        JSON.stringify({ detail: '인터뷰 세션을 찾을 수 없습니다.' }),
        { status: 404 }
      );
    }

    mockInterviewSessions.delete(body.session_id);

    return HttpResponse.json({
      status: 'completed',
      round: 1,
      interview_context: {
        experience_level: body.answers[0]?.answer || '초보자',
        daily_time: body.answers[1]?.answer || '1시간',
        motivation: body.answers[2]?.answer || '',
        topic: session.topic,
      },
    });
  }),

  // ============ 피드백 세션 시작 ============
  http.post(`${API_BASE}/feedback/start`, async ({ request }) => {
    const body = (await request.json()) as {
      roadmap_data: Record<string, unknown>;
      interview_context?: Record<string, unknown>;
    };

    await delay(500);

    const sessionId = `mock-feedback-session-${Date.now()}`;
    mockFeedbackSessions.set(sessionId, {
      roadmapData: body.roadmap_data,
      messages: [],
    });

    return HttpResponse.json({
      session_id: sessionId,
      welcome_message:
        '안녕하세요! 생성된 로드맵을 확인해주세요. 🎯\n\n수정이 필요한 부분이 있다면 말씀해주세요. 예를 들어:\n- "1주차가 너무 어려워요"\n- "실습 위주로 바꿔주세요"\n- "기간을 늘려주세요"\n\n마음에 드시면 확정 버튼을 눌러주세요!',
    });
  }),

  // ============ 피드백 메시지 전송 ============
  http.post(`${API_BASE}/feedback/:sessionId/message`, async ({ params, request }) => {
    const { sessionId } = params;
    const body = (await request.json()) as { message: string };

    const session = mockFeedbackSessions.get(sessionId as string);
    if (!session) {
      return new HttpResponse(
        JSON.stringify({ detail: '피드백 세션을 찾을 수 없습니다.' }),
        { status: 404 }
      );
    }

    await delay(1200);

    // 메시지에 따른 응답 생성
    const responseMap: Record<string, { response: string; hasModification: boolean }> = {
      '너무 어려워요': {
        response:
          '알겠습니다! 난이도를 낮춰서 더 기초적인 내용부터 시작하도록 수정했어요. 이제 부담 없이 학습하실 수 있을 거예요. 😊',
        hasModification: true,
      },
      '더 쉽게 해주세요': {
        response:
          '좀 더 쉬운 단계로 나누어서 진행할 수 있도록 조정했습니다. 천천히 하나씩 해결해 나가봐요!',
        hasModification: true,
      },
      '실습 위주로': {
        response:
          '실습 중심의 과제로 변경했어요! 직접 만들면서 배울 수 있도록 구성했습니다. 💪',
        hasModification: true,
      },
      '이론 위주로': {
        response:
          '이론적인 기반을 다질 수 있도록 개념 학습 위주로 수정했습니다. 탄탄한 기초가 중요하죠!',
        hasModification: true,
      },
      '기간 늘려주세요': {
        response:
          '각 주차별 학습량을 줄이고 여유 있게 진행할 수 있도록 조정했어요. 지치지 않고 꾸준히 할 수 있을 거예요.',
        hasModification: true,
      },
      '더 빡세게': {
        response:
          '학습 강도를 높여서 더 집중적으로 진행할 수 있도록 수정했습니다! 화이팅! 🔥',
        hasModification: true,
      },
    };

    const matchedResponse = responseMap[body.message] || {
      response: `"${body.message}" 피드백을 반영하여 로드맵을 검토했습니다. 다른 수정이 필요하시면 말씀해주세요! 😄`,
      hasModification: false,
    };

    // 메시지 저장
    session.messages.push({ role: 'user', content: body.message });
    session.messages.push({ role: 'assistant', content: matchedResponse.response });

    return HttpResponse.json({
      response: matchedResponse.response,
      modifications: matchedResponse.hasModification
        ? {
            monthly_goals: [{ month_number: 1, title: '수정된 1월차 목표', description: '수정된 설명' }],
          }
        : null,
      updated_roadmap: session.roadmapData,
    });
  }),

  // ============ 피드백 세션 확정 ============
  http.post(`${API_BASE}/feedback/:sessionId/finalize`, async ({ params }) => {
    const { sessionId } = params;

    const session = mockFeedbackSessions.get(sessionId as string);
    if (!session) {
      return new HttpResponse(
        JSON.stringify({ detail: '피드백 세션을 찾을 수 없습니다.' }),
        { status: 404 }
      );
    }

    await delay(1500);

    const roadmapId = `mock-roadmap-${Date.now()}`;
    mockFeedbackSessions.delete(sessionId as string);

    return HttpResponse.json({
      roadmap_id: roadmapId,
      title:
        (session.roadmapData as { title?: string })?.title || '나의 학습 로드맵',
    });
  }),

  // ============ 피드백 세션 취소 ============
  http.delete(`${API_BASE}/feedback/:sessionId`, async ({ params }) => {
    const { sessionId } = params;
    mockFeedbackSessions.delete(sessionId as string);

    return HttpResponse.json({
      message: '세션이 취소되었습니다.',
    });
  }),
];
