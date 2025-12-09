# LoadmapAI

AI 기반 개인화 학습 로드맵 생성 플랫폼

## 데모

**서비스 URL**: https://reseeall.com

| 테스트 계정 | |
|-------------|------------------|
| Email | `test@reseeall.com` |
| Password | `Test1234!` |

## 프로젝트 소개

LoadmapAI는 사용자의 학습 목표를 입력받아 AI가 맞춤형 월별/주별/일별 학습 계획을 자동 생성하는 서비스입니다. LangGraph 기반의 멀티 스텝 AI 파이프라인과 SSE 스트리밍을 활용하여 실시간으로 로드맵 생성 과정을 확인할 수 있습니다.

### 주요 기능

- **AI 인터뷰 기반 로드맵 생성**: 목표 설정 후 AI와의 대화를 통해 사용자 수준/선호도 파악
- **실시간 스트리밍 생성**: SSE를 통한 로드맵 생성 과정 실시간 미리보기
- **계층적 태스크 관리**: 월별 목표 → 주별 태스크 → 일별 태스크 드릴다운
- **진행률 추적**: 체크박스 기반 완료 처리 및 자동 진행률 계산
- **AI 채팅 수정**: 생성된 로드맵을 자연어로 수정 요청

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | FastAPI, Python 3.11, SQLAlchemy, Alembic |
| **AI/ML** | LangGraph, LangChain, Claude API (Anthropic) |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS |
| **상태관리** | Zustand, TanStack Query |
| **Database** | PostgreSQL 15, Redis 7 |
| **Auth** | JWT, OAuth2 (Google, GitHub) |
| **Infra** | Docker, Docker Compose |

## 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Zustand │  │ TanStack │  │   SSE    │  │  React Router    │ │
│  │  Stores  │  │  Query   │  │ Handler  │  │     Pages        │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP / SSE
┌─────────────────────────────▼───────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Layer (v1)                            ││
│  │  /auth  /oauth  /roadmaps  /roadmap_chat  /learning         ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Service Layer                              ││
│  │  RoadmapService  LearningService  AuthService               ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 AI Layer (LangGraph)                         ││
│  │  ┌──────────────────────────────────────────────────────┐   ││
│  │  │              Roadmap Generation Pipeline              │   ││
│  │  │  goal_analyzer → monthly_gen → weekly_gen → daily_gen │   ││
│  │  └──────────────────────────────────────────────────────┘   ││
│  │  ┌──────────────────────────────────────────────────────┐   ││
│  │  │               Interview Pipeline                      │   ││
│  │  │        question_gen → response_analyzer               │   ││
│  │  └──────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Data Layer                                ││
│  │  SQLAlchemy Models  │  Pydantic Schemas  │  Alembic         ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  PostgreSQL  │       │    Redis     │       │  Claude API  │
│   Database   │       │    Cache     │       │  (Anthropic) │
└──────────────┘       └──────────────┘       └──────────────┘
```

### 데이터 모델

```
Roadmap (로드맵)
  └── MonthlyGoal (월별 목표)
        └── WeeklyTask (주별 태스크)
              └── DailyTask (일별 태스크)
                    └── Question (학습 문제) - Learning Mode
```

### AI 파이프라인 (LangGraph)

로드맵 생성은 4단계의 순차적 LLM 호출로 구성됩니다:

1. **Goal Analyzer**: 목표 분석 및 인터뷰 컨텍스트 통합
2. **Monthly Generator**: 월별 학습 목표 생성 + SSE 스트리밍
3. **Weekly Generator**: 주별 세부 태스크 생성 + SSE 스트리밍
4. **Daily Generator**: 일별 실행 항목 생성 + DB 저장

```python
# LangGraph 상태 흐름
StateGraph(RoadmapGenerationState)
  .add_node("goal_analyzer", analyze_goal)
  .add_node("monthly_generator", generate_monthly)
  .add_node("weekly_generator", generate_weekly)
  .add_node("daily_generator", generate_daily)
  .add_edge(START, "goal_analyzer")
  .add_edge("goal_analyzer", "monthly_generator")
  .add_edge("monthly_generator", "weekly_generator")
  .add_edge("weekly_generator", "daily_generator")
  .add_edge("daily_generator", END)
```

### 주요 기술적 결정

| 결정 | 이유 |
|------|------|
| **LangGraph** | 복잡한 AI 워크플로우의 상태 관리 및 노드 간 데이터 전달 |
| **SSE (Server-Sent Events)** | 로드맵 생성 중 실시간 프리뷰 제공, POST 요청 지원 필요로 fetch 기반 구현 |
| **Zustand + TanStack Query** | 클라이언트 상태(auth)와 서버 상태(data fetching) 분리 |
| **ThreadPoolExecutor** | LangGraph 동기 실행을 FastAPI 비동기 환경에서 non-blocking 처리 |

## 프로젝트 구조

```
LoadmapAI/
├── backend/
│   ├── app/
│   │   ├── ai/                 # LangGraph 파이프라인
│   │   │   ├── nodes/          # 개별 노드 로직
│   │   │   ├── prompts/        # AI 프롬프트 템플릿
│   │   │   ├── roadmap_graph.py
│   │   │   └── interview_graph.py
│   │   ├── api/v1/             # API 엔드포인트
│   │   ├── core/               # 보안, OAuth 설정
│   │   ├── models/             # SQLAlchemy 모델
│   │   ├── schemas/            # Pydantic 스키마
│   │   ├── services/           # 비즈니스 로직
│   │   └── main.py
│   ├── alembic/                # DB 마이그레이션
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React 컴포넌트
│   │   ├── hooks/              # 커스텀 훅 (useInterview, useStreamingGeneration)
│   │   ├── pages/              # 라우트 페이지
│   │   ├── stores/             # Zustand 스토어
│   │   └── types/              # TypeScript 타입
│   └── package.json
└── docker-compose.yml
```

## 실행 방법

### Docker (권장)

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일에서 ANTHROPIC_API_KEY 등 설정

# 실행
docker-compose up --build
```

### 로컬 개발

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 환경 변수

| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude AI API 키 |
| `DATABASE_URL` | PostgreSQL 연결 문자열 |
| `SECRET_KEY` | JWT 서명 키 |
| `DEV_MODE` | `true`: Haiku (비용 절감), `false`: Sonnet (품질) |

## API 문서

서버 실행 후: http://localhost:8000/docs (Swagger UI)
