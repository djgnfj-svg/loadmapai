# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LoadmapAI is an AI-powered learning roadmap management platform. Users input learning goals and the AI generates personalized month/week/day learning plans using Claude AI via LangGraph.

## Development Commands

### Docker (Recommended)
```bash
docker-compose up --build       # Build and start all services
docker-compose up -d            # Start in background
docker-compose logs -f          # View logs
docker-compose down             # Stop all services
```

### Backend (Python/FastAPI)
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head            # Run database migrations
uvicorn app.main:app --reload --port 8000   # Start dev server
pytest                          # Run all tests
pytest tests/api/test_auth.py   # Run single test file
pytest -k "test_login"          # Run tests matching pattern
```

### Frontend (React/TypeScript)
```bash
cd frontend
npm install
npm run dev                     # Start dev server (port 3000)
npm run build                   # Build for production (includes tsc)
npm run lint                    # ESLint check
npm test                        # Run vitest
npm run test:coverage           # Run with coverage
```

## Architecture

### Backend (FastAPI + LangGraph)
- **Entry point**: `app/main.py` - FastAPI app with CORS, session middleware, exception handlers
- **API routes**: `app/api/v1/` - Versioned API with auth, oauth, roadmaps, roadmap_chat endpoints
- **AI workflow**: `app/ai/roadmap_graph.py` - LangGraph pipeline with 4 sequential LLM calls:
  - `goal_analyzer` → `monthly_generator` → `weekly_generator` → `daily_generator` → `saver`
- **State management**: `app/ai/state.py` - TypedDict `RoadmapGenerationState` passed through LangGraph
- **Models**: SQLAlchemy models in `app/models/` - User, Roadmap, MonthlyGoal, WeeklyTask, DailyTask
- **Config**: `app/config.py` - Pydantic Settings with env vars

### Frontend (React + TypeScript)
- **State**: Zustand stores in `src/stores/` (authStore, toastStore, themeStore)
- **Data fetching**: TanStack Query hooks in `src/hooks/` (useAuth, useRoadmaps, useRoadmapEdit)
- **Components**:
  - `src/components/common/` - Reusable UI (Button, Card, Modal, Input, Toast)
  - `src/components/tasks/` - Drilldown views (MonthlyGoalView → WeeklyTaskView → DailyTaskView)
  - `src/components/edit/` - Chat panel and task editing modals
- **Pages**: `src/pages/` - Route components (Dashboard, RoadmapList, RoadmapDetail, RoadmapCreate)
- **Types**: `src/types/index.ts` - Shared TypeScript interfaces mirroring backend schemas

### Data Model Hierarchy
```
Roadmap (1-6 months)
  └── MonthlyGoal
        └── WeeklyTask
              └── DailyTask
```

### Key Patterns
- Backend tests use real PostgreSQL (via docker), not SQLite - see `tests/conftest.py`
- LangGraph runs synchronously in a ThreadPoolExecutor to avoid blocking FastAPI's event loop
- Frontend uses MSW for API mocking in tests (`src/mocks/`)
- DEV_MODE env var switches between Claude Haiku (cost-saving) and Sonnet (quality)

## Environment Variables

Required in `.env`:
- `ANTHROPIC_API_KEY` - For Claude AI
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - JWT signing
- `DEV_MODE` - `true` for Haiku, `false` for Sonnet

Optional for OAuth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

## Working Guidelines

* Always read entire files before making changes
* Commit early and often at logical milestones
* Look up external library syntax via Perplexity or web search if unsure
* Run linting after major changes
* Get Plan approved before writing code for new features
* Do not carry out large refactors unless explicitly instructed
* Break down large tasks and ask for clarification when needed