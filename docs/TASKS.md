# LoadmapAI - 개발 체크리스트

> 각 태스크 완료 시 체크박스를 표시하고 Git 커밋합니다.
> 커밋 메시지 형식: `[Phase X.X] 태스크 설명`

---

## Phase 1: 프로젝트 기반 구축 ✅

### 1.1 프로젝트 구조 생성
- [x] 루트 디렉토리 구조 생성
- [x] backend/ 디렉토리 구조 생성
- [x] frontend/ 디렉토리 구조 생성
- [x] .gitignore 파일 생성
- [x] .env.example 파일 생성

### 1.2 Docker Compose 설정
- [x] docker-compose.yml 작성
- [x] backend/Dockerfile 작성
- [x] frontend/Dockerfile 작성
- [x] Docker 네트워크 설정 확인
- [ ] `docker-compose up` 테스트

### 1.3 FastAPI 기본 설정
- [x] requirements.txt 작성
- [x] app/main.py 생성 (FastAPI 앱)
- [x] app/config.py 생성 (환경변수 설정)
- [x] CORS 미들웨어 설정
- [x] Health check 엔드포인트 (`/health`)

### 1.4 데이터베이스 연결
- [x] app/db/database.py 생성 (SQLAlchemy 설정)
- [x] alembic init 실행
- [x] alembic.ini 설정
- [x] alembic/env.py 설정
- [ ] 첫 마이그레이션 테스트

### 1.5 React 프로젝트 설정
- [x] `npm create vite@latest` 실행
- [x] TypeScript 설정
- [x] TailwindCSS 설치 및 설정
- [x] 기본 폴더 구조 생성 (components, pages, hooks, services, store, types)
- [ ] `npm run dev` 테스트

### 1.6 API 클라이언트 설정
- [x] Axios 설치
- [x] services/api.ts 생성 (Axios 인스턴스)
- [x] 인터셉터 설정 (토큰 자동 추가)
- [x] 에러 핸들링 설정

---

## Phase 2: 인증 시스템 ✅

### 2.1 User 모델 생성
- [x] app/models/user.py 작성
- [x] Alembic 마이그레이션 생성
- [ ] 마이그레이션 실행 및 확인

### 2.2 이메일 회원가입/로그인 API
- [x] app/schemas/user.py 작성 (Pydantic)
- [x] app/core/security.py 작성 (비밀번호 해싱)
- [x] app/services/auth_service.py 작성
- [x] POST /api/v1/auth/register 구현
- [x] POST /api/v1/auth/login 구현
- [ ] Postman/curl 테스트

### 2.3 JWT 미들웨어
- [x] JWT 토큰 생성 함수 (access, refresh)
- [x] JWT 토큰 검증 함수
- [x] app/api/deps.py 작성 (get_current_user)
- [x] POST /api/v1/auth/refresh 구현
- [ ] 보호된 엔드포인트 테스트

### 2.4 Google/GitHub OAuth 연동
- [x] app/core/oauth.py 작성
- [x] GET /api/v1/auth/google 구현
- [x] GET /api/v1/auth/google/callback 구현
- [x] GET /api/v1/auth/github 구현
- [x] GET /api/v1/auth/github/callback 구현
- [ ] OAuth 플로우 테스트

### 2.5 프론트엔드 인증 페이지 및 상태 관리
- [x] Zustand 설치
- [x] store/authStore.ts 작성
- [x] services/authService.ts 작성
- [x] pages/Login.tsx 구현
- [x] pages/Register.tsx 구현
- [x] 로그인 상태 유지 (localStorage)
- [x] 로그아웃 기능

---

## Phase 3: 기본 데이터 모델 및 CRUD ✅

### 3.1 Roadmap 모델
- [x] app/models/roadmap.py 작성 (mode 필드 포함)
- [x] app/schemas/roadmap.py 작성
- [x] Alembic 마이그레이션

### 3.2 Milestone, WeeklyTask, DailyTask 모델
- [x] app/models/milestone.py 작성
- [x] app/models/weekly_task.py 작성
- [x] app/models/daily_task.py 작성
- [x] 각 스키마 파일 작성
- [x] Alembic 마이그레이션
- [x] 관계 설정 확인 (cascade)

### 3.3 기본 CRUD API
- [x] GET /api/v1/roadmaps (목록)
- [x] POST /api/v1/roadmaps (생성)
- [x] GET /api/v1/roadmaps/{id} (상세)
- [x] GET /api/v1/roadmaps/{id}/full (전체 계층)
- [x] PATCH /api/v1/roadmaps/{id} (수정)
- [x] DELETE /api/v1/roadmaps/{id} (삭제)
- [ ] Milestone CRUD API
- [ ] WeeklyTask CRUD API
- [ ] DailyTask CRUD API

### 3.4 일별 태스크 체크 기능
- [x] PATCH /api/v1/daily-tasks/{id}/check 구현
- [x] 진행률 자동 계산 로직 구현
- [ ] 테스트

---

## Phase 4: LangGraph - 로드맵 생성 ✅

### 4.1 LangGraph 기본 설정
- [x] langraph, langchain-anthropic 설치
- [x] app/ai/state.py 작성 (GraphState)
- [x] Claude API 연결 테스트

### 4.2 Goal Analyzer → Daily Task Generator 노드
- [x] app/ai/nodes/goal_analyzer.py 작성
- [x] app/ai/nodes/monthly_generator.py 작성
- [x] app/ai/nodes/weekly_generator.py 작성
- [x] app/ai/nodes/daily_generator.py 작성
- [x] app/ai/prompts/templates.py 작성

### 4.3 Validator 노드
- [x] app/ai/nodes/validator.py 작성
- [x] 검증 실패 시 재생성 로직

### 4.4 `/generate` API 엔드포인트
- [x] app/ai/roadmap_graph.py 작성 (그래프 통합)
- [x] POST /api/v1/roadmaps/generate 구현
- [x] app/ai/nodes/saver.py 작성 (DB 저장)
- [ ] Rate Limiting 적용
- [ ] 테스트 (1개월, 3개월, 6개월)

---

## Phase 5: 프론트엔드 기본 UI ✅

### 5.1 공통/레이아웃 컴포넌트
- [x] components/layout/Header.tsx
- [x] components/common/Button.tsx
- [x] components/common/Input.tsx
- [x] components/common/Modal.tsx
- [x] components/common/Card.tsx
- [x] components/common/Loading.tsx
- [x] components/common/Progress.tsx
- [x] components/layout/Sidebar.tsx
- [x] components/layout/Layout.tsx

### 5.2 랜딩, 대시보드 페이지
- [x] pages/Landing.tsx (Home.tsx)
- [x] pages/Dashboard.tsx
- [x] 오늘의 할 일 컴포넌트
- [x] 진행률 표시 컴포넌트 (CircularProgress)

### 5.3 로드맵 생성 페이지 (모드 선택 UI)
- [x] pages/RoadmapCreate.tsx
- [x] 모드 선택 UI (플래닝/러닝)
- [x] 목표 입력 폼
- [x] 기간/시간 선택
- [x] AI 생성 버튼 + 로딩 상태
- [x] 생성 완료 후 리다이렉트

### 5.4 드릴다운 컴포넌트 (월/주/일)
- [x] components/tasks/DrilldownContainer.tsx
- [x] components/tasks/MonthlyGoalView.tsx
- [x] components/tasks/WeeklyTaskView.tsx
- [x] components/tasks/DailyTaskView.tsx
- [x] 펼치기/접기 애니메이션
- [x] 진행률 바 표시

### 5.5 로드맵 상세 페이지
- [x] pages/RoadmapDetail.tsx
- [x] pages/RoadmapList.tsx
- [x] 드릴다운 컨테이너 통합
- [x] 태스크 체크박스 기능
- [ ] API 연동 테스트

---

## Phase 6: 러닝 모드 - 퀴즈 시스템

### 6.1 Quiz, Question, UserAnswer 모델
- [ ] app/models/quiz.py 작성
- [ ] app/models/question.py 작성
- [ ] app/models/user_answer.py 작성
- [ ] 스키마 파일 작성
- [ ] Alembic 마이그레이션

### 6.2 LangGraph - 문제 생성 그래프
- [ ] app/ai/nodes/topic_analyzer.py 작성
- [ ] app/ai/nodes/question_generator.py 작성 (객관식/단답형/서술형)
- [ ] app/ai/nodes/quality_validator.py 작성
- [ ] app/ai/question_graph.py 작성

### 6.3 LangGraph - 채점 그래프
- [ ] app/ai/nodes/answer_analyzer.py 작성
- [ ] app/ai/nodes/feedback_generator.py 작성
- [ ] app/ai/nodes/score_calculator.py 작성
- [ ] app/ai/grading_graph.py 작성

### 6.4 퀴즈 API 엔드포인트
- [ ] GET /api/v1/quizzes/daily-task/{id} 구현
- [ ] POST /api/v1/quizzes/daily-task/{id}/generate 구현
- [ ] GET /api/v1/quizzes/{id} 구현
- [ ] POST /api/v1/quizzes/{id}/start 구현
- [ ] POST /api/v1/quizzes/{id}/complete 구현
- [ ] POST /api/v1/questions/{id}/answer 구현

### 6.5 퀴즈 풀이 페이지
- [ ] pages/QuizPage.tsx
- [ ] components/quiz/QuestionView.tsx
- [ ] components/quiz/AnswerInput.tsx (유형별)
- [ ] 문제 네비게이션
- [ ] 제출 기능

### 6.6 결과/피드백 페이지
- [ ] pages/QuizResult.tsx
- [ ] components/quiz/FeedbackView.tsx
- [ ] 점수 표시
- [ ] 오답 분석
- [ ] [복습하기] 버튼

---

## Phase 7: 마무리

### 7.1 에러 핸들링
- [ ] 백엔드 전역 에러 핸들러
- [ ] 프론트엔드 에러 바운더리
- [ ] 사용자 친화적 에러 메시지
- [ ] 네트워크 에러 처리

### 7.2 로딩 상태 UI
- [ ] 스켈레톤 컴포넌트
- [ ] 로딩 스피너
- [ ] AI 생성 중 프로그레스 표시

### 7.3 반응형 디자인
- [ ] 모바일 레이아웃
- [ ] 태블릿 레이아웃
- [ ] 터치 인터랙션 최적화

### 7.4 README 작성
- [ ] 프로젝트 소개
- [ ] 설치 방법
- [ ] 환경변수 설정
- [ ] 실행 방법
- [ ] API 문서 링크

---

## 커밋 이력

| 커밋 | Phase | 날짜 | 설명 |
|------|-------|------|------|
| 319c8c2 | 1.2 | 2024 | Docker Compose 개발 환경 설정 |
| 4d6f1be | 1.3 | 2024 | FastAPI 기본 설정 및 프로젝트 구조 |
| 5e97fca | 1.4 | 2024 | 데이터베이스 연결 및 Alembic 설정 |
| bfb434e | 1.5 | 2024 | React 프로젝트 기본 구조 설정 |
| 074a8b8 | 1.6 | 2024 | API 클라이언트 및 React Query 훅 설정 |
| 4702f64 | 2.1 | 2024 | User 모델 및 마이그레이션 생성 |
| 23d0d63 | 2.2 | 2024 | 이메일 회원가입/로그인 API 구현 |
| 1cb6b83 | 2.3 | 2024 | JWT 인증 미들웨어 및 보호된 엔드포인트 |
| 61789d2 | 2.4 | 2024 | Google/GitHub OAuth 연동 |
| 013e576 | 2.5 | 2024 | 프론트엔드 인증 API 연동 |
| 846e158 | 3.1-3.2 | 2024 | 로드맵 및 계층 데이터 모델 생성 |
| c2a930b | 3.3-3.4 | 2024 | 로드맵 CRUD API 및 태스크 체크 기능 |
| 87a325f | 4.1-4.4 | 2024 | LangGraph AI 로드맵 생성 시스템 |
| dab16e2 | 5.1-5.5 | 2024 | 프론트엔드 기본 UI (공통 컴포넌트, 대시보드, 로드맵 페이지) |

---

## 참고사항

- **기간 제한**: 로드맵은 1-6개월만 가능
- **문제 유형**: 객관식, 단답형, 서술형 (코딩 X)
- **퀴즈당 문제 수**: 5-10문제
- **AI Rate Limit**: 로드맵 5회/일, 퀴즈 20회/일
