from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import date

from app.db import get_db
from app.models.user import User
from app.models.roadmap import RoadmapMode
from app.schemas import (
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapResponse,
    RoadmapWithMonthly,
    RoadmapFull,
    RoadmapScheduleUpdate,
    RoadmapFinalizeResponse,
    MonthlyGoalCreate,
    MonthlyGoalUpdate,
    MonthlyGoalResponse,
    WeeklyTaskCreate,
    WeeklyTaskUpdate,
    WeeklyTaskResponse,
    DailyTaskCreate,
    DailyTaskUpdate,
    DailyTaskResponse,
    DailyTaskReorderRequest,
)
from app.services.roadmap_service import (
    RoadmapService,
    DailyTaskService,
    MonthlyGoalService,
    WeeklyTaskService,
)
from app.api.deps import get_current_user
from app.ai.roadmap_graph import (
    generate_roadmap,
    generate_roadmap_with_context,
    generate_roadmap_from_interview,
)
from app.ai.nodes.interview_generator import generate_interview_questions
from app.services.interview_service import InterviewService
from app.models.interview_session import InterviewStatus


# ============ Interview Request/Response Models ============

class InterviewStartRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    mode: RoadmapMode = RoadmapMode.PLANNING
    duration_months: int = Field(..., ge=1, le=6)


class InterviewQuestionResponse(BaseModel):
    id: str
    question: str
    question_type: str
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None


class InterviewStartResponse(BaseModel):
    questions: List[InterviewQuestionResponse]


class InterviewAnswer(BaseModel):
    question_id: str
    answer: str


class RoadmapGenerateWithContextRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    mode: RoadmapMode = RoadmapMode.PLANNING
    interview_answers: List[InterviewAnswer]
    interview_questions: List[InterviewQuestionResponse]


# ============ Standard Request/Response Models ============

class RoadmapGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    mode: RoadmapMode = RoadmapMode.PLANNING


class RoadmapGenerateResponse(BaseModel):
    roadmap_id: str
    title: str
    message: str


class RoadmapFromInterviewRequest(BaseModel):
    """Request to generate roadmap from completed interview session."""
    interview_session_id: UUID
    start_date: date
    use_web_search: bool = True

router = APIRouter()


@router.get("", response_model=List[RoadmapResponse])
async def list_roadmaps(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of user's roadmaps."""
    service = RoadmapService(db)
    return service.get_roadmaps(current_user.id, skip, limit)


@router.post("", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    data: RoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new roadmap (without AI generation)."""
    service = RoadmapService(db)
    return service.create_roadmap(current_user.id, data)


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific roadmap."""
    service = RoadmapService(db)
    roadmap = service.get_roadmap(roadmap_id, current_user.id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )
    return roadmap


@router.get("/{roadmap_id}/monthly", response_model=RoadmapWithMonthly)
async def get_roadmap_with_monthly(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get roadmap with monthly goals."""
    service = RoadmapService(db)
    roadmap = service.get_roadmap_with_monthly(roadmap_id, current_user.id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )
    return roadmap


@router.get("/{roadmap_id}/full", response_model=RoadmapFull)
async def get_roadmap_full(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full roadmap with all hierarchy (monthly -> weekly -> daily)."""
    service = RoadmapService(db)
    roadmap = service.get_roadmap_full(roadmap_id, current_user.id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )
    return roadmap


@router.patch("/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: UUID,
    data: RoadmapUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a roadmap."""
    service = RoadmapService(db)
    return service.update_roadmap(roadmap_id, current_user.id, data)


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a roadmap."""
    service = RoadmapService(db)
    service.delete_roadmap(roadmap_id, current_user.id)


@router.patch("/daily-tasks/{task_id}/toggle", response_model=DailyTaskResponse)
async def toggle_daily_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle daily task check status."""
    service = DailyTaskService(db)
    return service.toggle_daily_task(task_id, current_user.id)


@router.post("/generate", response_model=RoadmapGenerateResponse)
async def generate_roadmap_endpoint(
    data: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a complete roadmap using AI (LangGraph + Claude)."""
    try:
        result = await generate_roadmap(
            topic=data.topic,
            duration_months=data.duration_months,
            start_date=data.start_date,
            mode=data.mode,
            user_id=str(current_user.id),
            db=db,
        )

        return RoadmapGenerateResponse(
            roadmap_id=result["roadmap_id"],
            title=result["title"],
            message="로드맵이 성공적으로 생성되었습니다.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로드맵 생성 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(
    data: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate personalized interview questions based on topic and mode."""
    try:
        questions = generate_interview_questions(
            topic=data.topic,
            mode=data.mode.value,
            duration_months=data.duration_months,
        )

        return InterviewStartResponse(
            questions=[
                InterviewQuestionResponse(
                    id=q["id"],
                    question=q["question"],
                    question_type=q["question_type"],
                    options=q.get("options"),
                    placeholder=q.get("placeholder"),
                )
                for q in questions
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인터뷰 질문 생성 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/generate-with-context", response_model=RoadmapGenerateResponse)
async def generate_roadmap_with_context_endpoint(
    data: RoadmapGenerateWithContextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a complete roadmap using AI with interview context."""
    try:
        # Convert to dict format for the function
        answers = [{"question_id": a.question_id, "answer": a.answer} for a in data.interview_answers]
        questions = [
            {
                "id": q.id,
                "question": q.question,
                "question_type": q.question_type,
                "options": q.options,
                "placeholder": q.placeholder,
            }
            for q in data.interview_questions
        ]

        result = await generate_roadmap_with_context(
            topic=data.topic,
            duration_months=data.duration_months,
            start_date=data.start_date,
            mode=data.mode,
            user_id=str(current_user.id),
            interview_answers=answers,
            interview_questions=questions,
            db=db,
        )

        return RoadmapGenerateResponse(
            roadmap_id=result["roadmap_id"],
            title=result["title"],
            message="맞춤형 로드맵이 성공적으로 생성되었습니다.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로드맵 생성 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/generate-from-interview", response_model=RoadmapGenerateResponse)
async def generate_roadmap_from_interview_endpoint(
    data: RoadmapFromInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a roadmap from a completed deep interview session.

    This endpoint:
    1. Takes a completed interview session ID
    2. Uses the compiled interview context
    3. Optionally performs web search for latest info
    4. Generates a personalized roadmap
    """
    interview_service = InterviewService(db)

    # Get interview session
    session = interview_service.get_session(data.interview_session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인터뷰 세션을 찾을 수 없습니다.",
        )

    # Check if interview is completed
    if session.status != InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인터뷰가 완료되지 않았습니다. 먼저 인터뷰를 완료해주세요.",
        )

    # Check if already has a roadmap
    if session.roadmap_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 이 인터뷰로 생성된 로드맵이 있습니다.",
        )

    try:
        # Get mode enum
        mode = RoadmapMode.LEARNING if session.mode == "learning" else RoadmapMode.PLANNING

        result = await generate_roadmap_from_interview(
            topic=session.topic,
            duration_months=session.duration_months,
            start_date=data.start_date,
            mode=mode,
            user_id=str(current_user.id),
            compiled_context=session.compiled_context or "",
            daily_minutes=session.extracted_daily_minutes,
            rest_days=session.extracted_rest_days,
            intensity=session.extracted_intensity,
            db=db,
            use_web_search=data.use_web_search,
        )

        # Link roadmap to interview session
        interview_service.link_roadmap(
            session_id=session.id,
            roadmap_id=UUID(result["roadmap_id"]),
            user_id=current_user.id,
        )

        return RoadmapGenerateResponse(
            roadmap_id=result["roadmap_id"],
            title=result["title"],
            message="딥 인터뷰 기반 맞춤형 로드맵이 생성되었습니다.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로드맵 생성 중 오류가 발생했습니다: {str(e)}",
        )


# ============ Roadmap Finalization & Schedule ============

@router.post("/{roadmap_id}/finalize", response_model=RoadmapFinalizeResponse)
async def finalize_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """로드맵 확정"""
    service = RoadmapService(db)
    roadmap = service.finalize_roadmap(roadmap_id, current_user.id)
    return RoadmapFinalizeResponse(
        id=roadmap.id,
        is_finalized=roadmap.is_finalized,
        finalized_at=roadmap.finalized_at,
        message="로드맵이 확정되었습니다.",
    )


@router.post("/{roadmap_id}/unfinalize", response_model=RoadmapFinalizeResponse)
async def unfinalize_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """로드맵 확정 해제"""
    service = RoadmapService(db)
    roadmap = service.unfinalize_roadmap(roadmap_id, current_user.id)
    return RoadmapFinalizeResponse(
        id=roadmap.id,
        is_finalized=roadmap.is_finalized,
        finalized_at=roadmap.finalized_at,
        message="로드맵 확정이 해제되었습니다.",
    )


@router.patch("/{roadmap_id}/schedule", response_model=RoadmapResponse)
async def update_roadmap_schedule(
    roadmap_id: UUID,
    data: RoadmapScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """로드맵 스케줄 설정 업데이트"""
    service = RoadmapService(db)
    return service.update_schedule(roadmap_id, current_user.id, data)


# ============ Monthly Goal CRUD ============

@router.post("/{roadmap_id}/monthly-goals", response_model=MonthlyGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_monthly_goal(
    roadmap_id: UUID,
    data: MonthlyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """월별 목표 생성"""
    service = MonthlyGoalService(db)
    return service.create_monthly_goal(roadmap_id, current_user.id, data)


@router.patch("/monthly-goals/{goal_id}", response_model=MonthlyGoalResponse)
async def update_monthly_goal(
    goal_id: UUID,
    data: MonthlyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """월별 목표 수정"""
    service = MonthlyGoalService(db)
    return service.update_monthly_goal(goal_id, current_user.id, data)


@router.delete("/monthly-goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monthly_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """월별 목표 삭제"""
    service = MonthlyGoalService(db)
    service.delete_monthly_goal(goal_id, current_user.id)


# ============ Weekly Task CRUD ============

@router.post("/monthly-goals/{goal_id}/weekly-tasks", response_model=WeeklyTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_weekly_task(
    goal_id: UUID,
    data: WeeklyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크 생성"""
    service = WeeklyTaskService(db)
    return service.create_weekly_task(goal_id, current_user.id, data)


@router.patch("/weekly-tasks/{task_id}", response_model=WeeklyTaskResponse)
async def update_weekly_task(
    task_id: UUID,
    data: WeeklyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크 수정"""
    service = WeeklyTaskService(db)
    return service.update_weekly_task(task_id, current_user.id, data)


@router.delete("/weekly-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크 삭제"""
    service = WeeklyTaskService(db)
    service.delete_weekly_task(task_id, current_user.id)


# ============ Daily Task CRUD ============

@router.post("/weekly-tasks/{task_id}/daily-tasks", response_model=DailyTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_task(
    task_id: UUID,
    data: DailyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일일 태스크 생성"""
    service = DailyTaskService(db)
    return service.create_daily_task(task_id, current_user.id, data)


@router.patch("/daily-tasks/{task_id}", response_model=DailyTaskResponse)
async def update_daily_task(
    task_id: UUID,
    data: DailyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일일 태스크 수정"""
    service = DailyTaskService(db)
    return service.update_daily_task(task_id, current_user.id, data)


@router.delete("/daily-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일일 태스크 삭제"""
    service = DailyTaskService(db)
    service.delete_daily_task(task_id, current_user.id)


@router.post("/daily-tasks/reorder", response_model=List[DailyTaskResponse])
async def reorder_daily_tasks(
    data: DailyTaskReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """일일 태스크 순서 변경"""
    service = DailyTaskService(db)
    return service.reorder_daily_tasks(data, current_user.id)
