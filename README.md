# LoadmapAI

AI 기반 학습 로드맵 관리 플랫폼

## 소개

LoadmapAI는 AI를 활용하여 개인화된 학습 로드맵을 생성하고 관리하는 플랫폼입니다. 학습 목표를 입력하면 AI가 월별, 주별, 일별 학습 계획을 자동으로 생성해주며, 퀴즈 기능을 통해 학습 내용을 점검할 수 있습니다.

### 주요 기능

- **AI 로드맵 생성**: Claude AI를 활용한 맞춤형 학습 계획 자동 생성
- **계층적 태스크 관리**: 월별 목표 → 주별 태스크 → 일별 태스크의 체계적 관리
- **진행률 추적**: 실시간 학습 진행률 확인 및 시각화
- **퀴즈 시스템**: AI가 생성한 퀴즈로 학습 내용 점검 (객관식, 단답형, 서술형)
- **AI 피드백**: 퀴즈 답변에 대한 상세한 AI 피드백 제공

## 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy + Alembic
- **Cache**: Redis 7
- **AI**: LangGraph + LangChain + Claude API (Anthropic)
- **Authentication**: JWT + OAuth2 (Google, GitHub)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Data Fetching**: React Query (TanStack Query)
- **Routing**: React Router v6

### Infrastructure
- **Containerization**: Docker + Docker Compose

## 시작하기

### 사전 요구사항

- Docker & Docker Compose
- Node.js 18+ (로컬 개발 시)
- Python 3.11+ (로컬 개발 시)

### 환경 변수 설정

1. 루트 디렉토리에 `.env` 파일 생성:

```bash
cp .env.example .env
```

2. `.env` 파일 수정:

```env
# Database
POSTGRES_USER=loadmap
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=loadmap_db
DATABASE_URL=postgresql://loadmap:your_secure_password@db:5432/loadmap_db

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Anthropic (Claude AI)
ANTHROPIC_API_KEY=your_anthropic_api_key

# OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Frontend
FRONTEND_URL=http://localhost:5173
VITE_API_URL=http://localhost:8000
```

### Docker로 실행

```bash
# 컨테이너 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 로컬 개발 환경

#### Backend

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build
```

## 프로젝트 구조

```
LoadmapAI/
├── backend/
│   ├── app/
│   │   ├── ai/                 # AI/LangGraph 관련
│   │   │   ├── nodes/          # LangGraph 노드
│   │   │   ├── prompts/        # AI 프롬프트 템플릿
│   │   │   ├── roadmap_graph.py
│   │   │   ├── question_graph.py
│   │   │   └── grading_graph.py
│   │   ├── api/v1/             # API 엔드포인트
│   │   ├── core/               # 핵심 설정 (보안, OAuth 등)
│   │   ├── db/                 # 데이터베이스 설정
│   │   ├── models/             # SQLAlchemy 모델
│   │   ├── schemas/            # Pydantic 스키마
│   │   ├── services/           # 비즈니스 로직
│   │   └── main.py
│   ├── alembic/                # 마이그레이션
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React 컴포넌트
│   │   │   ├── common/         # 공통 컴포넌트
│   │   │   ├── layout/         # 레이아웃 컴포넌트
│   │   │   ├── tasks/          # 태스크 관련 컴포넌트
│   │   │   └── quiz/           # 퀴즈 관련 컴포넌트
│   │   ├── hooks/              # 커스텀 훅
│   │   ├── lib/                # 유틸리티
│   │   ├── pages/              # 페이지 컴포넌트
│   │   ├── stores/             # Zustand 스토어
│   │   ├── types/              # TypeScript 타입
│   │   └── App.tsx
│   └── package.json
├── docs/
│   ├── PRD.md                  # 제품 요구사항 문서
│   └── TASKS.md                # 개발 체크리스트
├── docker-compose.yml
└── README.md
```

## API 문서

서버 실행 후 아래 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 API 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | 회원가입 |
| POST | `/api/v1/auth/login` | 로그인 |
| GET | `/api/v1/roadmaps` | 로드맵 목록 |
| POST | `/api/v1/roadmaps/generate` | AI 로드맵 생성 |
| GET | `/api/v1/roadmaps/{id}/full` | 로드맵 전체 조회 |
| PATCH | `/api/v1/roadmaps/daily-tasks/{id}/toggle` | 일별 태스크 완료 토글 |
| POST | `/api/v1/quizzes/daily-task/{id}/generate` | 퀴즈 생성 |
| POST | `/api/v1/quizzes/{id}/submit` | 퀴즈 제출 |
| POST | `/api/v1/quizzes/{id}/grade` | 퀴즈 채점 |

## 제약 사항

- **로드맵 기간**: 1-6개월
- **퀴즈 문제 유형**: 객관식, 단답형, 서술형 (코딩 문제 제외)
- **퀴즈당 문제 수**: 5-10문제

## 라이선스

MIT License
