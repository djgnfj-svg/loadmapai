import { http, HttpResponse, delay } from 'msw';

const API_BASE = '/api/v1';

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

  // ============ 로드맵 생성 (REST) ============
  http.post(`${API_BASE}/roadmaps/generate`, async () => {
    await delay(2000); // Simulate AI generation time

    return HttpResponse.json({
      roadmap_id: 'mock-roadmap-' + Date.now(),
      title: '나의 학습 로드맵',
      message: '로드맵이 성공적으로 생성되었습니다.',
    });
  }),
];
