# LoadmapAI - 개발 체크리스트

> 각 태스크 완료 시 체크박스를 표시하고 Git 커밋합니다.
> 커밋 메시지 형식: `[Phase X.X] 태스크 설명`

---

## Phase 1: 프로젝트 기반 구축

### 1.1 프로젝트 구조 생성
- [ ] 루트 디렉토리 구조 생성
- [ ] backend/ 디렉토리 구조 생성
- [ ] frontend/ 디렉토리 구조 생성
- [ ] .gitignore 파일 생성
- [ ] .env.example 파일 생성

### 1.2 Docker Compose 설정
- [ ] docker-compose.yml 작성
- [ ] backend/Dockerfile 작성
- [ ] frontend/Dockerfile 작성
- [ ] Docker 네트워크 설정 확인
- [ ] `docker-compose up` 테스트

### 1.3 FastAPI 기본 설정
- [ ] requirements.txt 작성
- [ ] app/main.py 생성 (FastAPI 앱)
- [ ] app/config.py 생성 (환경변수 설정)
- [ ] CORS 미들웨어 설정
- [ ] Health check 엔드포인트 (`/health`)

### 1.4 데이터베이스 연결
- [ ] app/db/database.py 생성 (SQLAlchemy 설정)
- [ ] alembic init 실행
- [ ] alembic.ini 설정
- [ ] alembic/env.py 설정
- [ ] 첫 마이그레이션 테스트

### 1.5 React 프로젝트 설정
- [ ] `npm create vite@latest` 실행
- [ ] TypeScript 설정
- [ ] TailwindCSS 설치 및 설정
- [ ] 기본 폴더 구조 생성 (components, pages, hooks, services, store, types)
- [ ] `npm run dev` 테스트

### 1.6 API 클라이언트 설정
- [ ] Axios 설치
- [ ] services/api.ts 생성 (Axios 인스턴스)
- [ ] 인터셉터 설정 (토큰 자동 추가)
- [ ] 에러 핸들링 설정

---

## Phase 2: 인증 시스템

### 2.1 User 모델 생성
- [ ] app/models/user.py 작성
- [ ] Alembic 마이그레이션 생성
- [ ] 마이그레이션 실행 및 확인

### 2.2 이메일 회원가입/로그인 API
- [ ] app/schemas/user.py 작성 (Pydantic)
- [ ] app/core/security.py 작성 (비밀번호 해싱)
- [ ] app/services/auth_service.py 작성
- [ ] POST /api/v1/auth/register 구현
- [ ] POST /api/v1/auth/login 구현
- [ ] Postman/curl 테스트

### 2.3 JWT 미들웨어
- [ ] JWT 토큰 생성 함수 (access, refresh)
- [ ] JWT 토큰 검증 함수
- [ ] app/api/deps.py 작성 (get_current_user)
- [ ] POST /api/v1/auth/refresh 구현
- [ ] 보호된 엔드포인트 테스트

### 2.4 Google/GitHub OAuth 연동
- [ ] app/core/oauth.py 작성
- [ ] GET /api/v1/auth/google 구현
- [ ] GET /api/v1/auth/google/callback 구현
- [ ] GET /api/v1/auth/github 구현
- [ ] GET /api/v1/auth/github/callback 구현
- [ ] OAuth 플로우 테스트

### 2.5 프론트엔드 인증 페이지 및 상태 관리
- [ ] Zustand 설치
- [ ] store/authStore.ts 작성
- [ ] services/authService.ts 작성
- [ ] pages/Login.tsx 구현
- [ ] pages/Register.tsx 구현
- [ ] 로그인 상태 유지 (localStorage)
- [ ] 로그아웃 기능

---

## Phase 3: 기본 데이터 모델 및 CRUD

### 3.1 Roadmap 모델
- [ ] app/models/roadmap.py 작성 (mode 필드 포함)
- [ ] app/schemas/roadmap.py 작성
- [ ] Alembic 마이그레이션

### 3.2 Milestone, WeeklyTask, DailyTask 모델
- [ ] app/models/milestone.py 작성
- [ ] app/models/weekly_task.py 작성
- [ ] app/models/daily_task.py 작성
- [ ] 각 스키마 파일 작성
- [ ] Alembic 마이그레이션
- [ ] 관계 설정 확인 (cascade)

### 3.3 기본 CRUD API
- [ ] GET /api/v1/roadmaps (목록)
- [ ] POST /api/v1/roadmaps (생성)
- [ ] GET /api/v1/roadmaps/{id} (상세)
- [ ] GET /api/v1/roadmaps/{id}/full (전체 계층)
- [ ] PATCH /api/v1/roadmaps/{id} (수정)
- [ ] DELETE /api/v1/roadmaps/{id} (삭제)
- [ ] Milestone CRUD API
- [ ] WeeklyTask CRUD API
- [ ] DailyTask CRUD API

### 3.4 일별 태스크 체크 기능
- [ ] PATCH /api/v1/daily-tasks/{id}/check 구현
- [ ] 진행률 자동 계산 로직 구현
- [ ] 테스트

---

## Phase 4: LangGraph - 로드맵 생성

### 4.1 LangGraph 기본 설정
- [ ] langraph, langchain-anthropic 설치
- [ ] app/ai/state.py 작성 (GraphState)
- [ ] Claude API 연결 테스트

### 4.2 Goal Analyzer → Daily Task Generator 노드
- [ ] app/ai/nodes/goal_analyzer.py 작성
- [ ] app/ai/nodes/roadmap_planner.py 작성
- [ ] app/ai/nodes/milestone_generator.py 작성
- [ ] app/ai/nodes/weekly_task_generator.py 작성
- [ ] app/ai/nodes/daily_task_generator.py 작성
- [ ] app/ai/prompts/templates.py 작성

### 4.3 Validator 노드
- [ ] app/ai/nodes/validator.py 작성
- [ ] 검증 실패 시 재생성 로직

### 4.4 `/generate` API 엔드포인트
- [ ] app/ai/roadmap_graph.py 작성 (그래프 통합)
- [ ] POST /api/v1/roadmaps/generate 구현
- [ ] Rate Limiting 적용
- [ ] 생성 결과 DB 저장
- [ ] 테스트 (1개월, 3개월, 6개월)

---

## Phase 5: 프론트엔드 기본 UI

### 5.1 공통/레이아웃 컴포넌트
- [ ] components/common/Button.tsx
- [ ] components/common/Input.tsx
- [ ] components/common/Modal.tsx
- [ ] components/common/Card.tsx
- [ ] components/common/Loading.tsx
- [ ] components/layout/Header.tsx
- [ ] components/layout/Sidebar.tsx
- [ ] components/layout/Layout.tsx

### 5.2 랜딩, 대시보드 페이지
- [ ] pages/Landing.tsx
- [ ] pages/Dashboard.tsx
- [ ] 오늘의 할 일 컴포넌트
- [ ] 진행률 표시 컴포넌트

### 5.3 로드맵 생성 페이지 (모드 선택 UI)
- [ ] pages/RoadmapCreate.tsx
- [ ] 모드 선택 UI (플래닝/러닝)
- [ ] 목표 입력 폼
- [ ] 기간/시간 선택
- [ ] AI 생성 버튼 + 로딩 상태
- [ ] 생성 완료 후 리다이렉트

### 5.4 드릴다운 컴포넌트 (월/주/일)
- [ ] components/tasks/DrilldownContainer.tsx
- [ ] components/tasks/MilestoneView.tsx
- [ ] components/tasks/WeeklyTaskView.tsx
- [ ] components/tasks/DailyTaskView.tsx
- [ ] 펼치기/접기 애니메이션
- [ ] 진행률 바 표시

### 5.5 로드맵 상세 페이지
- [ ] pages/RoadmapDetail.tsx
- [ ] pages/RoadmapList.tsx
- [ ] 드릴다운 컨테이너 통합
- [ ] 태스크 체크박스 기능
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
| - | - | - | - |

---

## 참고사항

- **기간 제한**: 로드맵은 1-6개월만 가능
- **문제 유형**: 객관식, 단답형, 서술형 (코딩 X)
- **퀴즈당 문제 수**: 5-10문제
- **AI Rate Limit**: 로드맵 5회/일, 퀴즈 20회/일
