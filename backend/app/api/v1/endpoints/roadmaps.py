import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import date

from app.db import get_db
from app.config import settings
from app.models.user import User
from app.models.roadmap import Roadmap, RoadmapMode
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
from app.services.roadmap_service import RoadmapService
from app.services.daily_task_service import DailyTaskService
from app.services.monthly_goal_service import MonthlyGoalService
from app.services.weekly_task_service import WeeklyTaskService
from app.services.daily_generation_service import DailyGenerationService
from app.api.deps import get_current_user
from app.ai.roadmap_graph import generate_roadmap
from app.ai.roadmap_stream import generate_roadmap_streaming


# ============ Request/Response Models ============

class RoadmapGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    mode: RoadmapMode = RoadmapMode.PLANNING
    interview_context: Optional[dict] = None


class RoadmapGenerateResponse(BaseModel):
    roadmap_id: str
    title: str
    message: str


class DailyTasksGenerateRequest(BaseModel):
    force: bool = Field(default=False, description="이전 주 완료 체크 건너뛰기")


class DailyTasksGenerateResponse(BaseModel):
    weekly_task_id: str
    message: str
    daily_tasks_count: int


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


class DailyTaskToggleResponse(DailyTaskResponse):
    """Daily task toggle response with next week generation info."""
    next_week_generated: bool = False
    next_week_id: Optional[str] = None


@router.patch("/daily-tasks/{task_id}/toggle", response_model=DailyTaskToggleResponse)
async def toggle_daily_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle daily task check status.

    If the weekly task reaches 100% completion, automatically generates
    daily tasks for the next week.
    """
    service = DailyTaskService(db)
    task = service.toggle_daily_task(task_id, current_user.id)

    # Check if we should generate next week's daily tasks
    next_week_generated = False
    next_week_id = None

    # Get weekly task to check progress
    weekly_task = task.weekly_task
    if weekly_task.progress == 100:
        try:
            gen_service = DailyGenerationService(db)
            next_week = await gen_service.try_generate_next_week(
                weekly_task.id, current_user.id
            )
            if next_week:
                next_week_generated = True
                next_week_id = str(next_week.id)
        except Exception:
            # Silently fail - next week can be generated manually
            pass

    # Build response
    response_data = {
        "id": task.id,
        "weekly_task_id": task.weekly_task_id,
        "day_number": task.day_number,
        "order": task.order,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "is_checked": task.is_checked,
        "created_at": task.created_at,
        "next_week_generated": next_week_generated,
        "next_week_id": next_week_id,
    }
    return DailyTaskToggleResponse(**response_data)


@router.get("/generate/can-generate")
async def check_can_generate_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """오늘 로드맵 생성 가능 여부 확인 (베타 일일 제한)."""
    limit = settings.beta_daily_roadmap_limit

    if limit <= 0:
        return {"can_generate": True, "today_count": 0, "limit": 0, "reason": None}

    today_count = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        func.date(Roadmap.created_at) == date.today()
    ).count()

    can_generate = today_count < limit
    reason = None if can_generate else f"오늘 이미 {today_count}개의 로드맵을 생성했습니다. (일일 제한: {limit}개)"

    return {
        "can_generate": can_generate,
        "today_count": today_count,
        "limit": limit,
        "reason": reason,
    }


@router.post("/generate", response_model=RoadmapGenerateResponse)
async def generate_roadmap_endpoint(
    data: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a complete roadmap using AI (LangGraph + Claude)."""
    # 베타 일일 제한 체크
    limit = settings.beta_daily_roadmap_limit
    if limit > 0:
        today_count = db.query(Roadmap).filter(
            Roadmap.user_id == current_user.id,
            func.date(Roadmap.created_at) == date.today()
        ).count()

        if today_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"일일 로드맵 생성 한도를 초과했습니다. (오늘 {today_count}개 생성, 제한: {limit}개)",
            )

    try:
        result = await generate_roadmap(
            topic=data.topic,
            duration_months=data.duration_months,
            start_date=data.start_date,
            mode=data.mode,
            user_id=str(current_user.id),
            db=db,
            interview_context=data.interview_context,
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


@router.post("/generate-stream")
async def generate_roadmap_stream(
    data: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a complete roadmap using AI with SSE streaming.

    실시간으로 로드맵 생성 과정을 스트리밍합니다.
    월별 → 해당 월의 주간 순서로 생성하여 각 단계마다 이벤트를 발송합니다.

    SSE Events:
    - title_ready: 제목/설명 생성 완료
    - month_ready: 월별 목표 생성 완료
    - weeks_ready: 해당 월의 주간 과제 생성 완료
    - progress: 진행률 업데이트
    - warning: 경고 (부분 실패)
    - error: 에러 발생
    - complete: 전체 완료

    Returns:
        StreamingResponse: SSE 이벤트 스트림
    """
    # 베타 일일 제한 체크
    limit = settings.beta_daily_roadmap_limit
    if limit > 0:
        today_count = db.query(Roadmap).filter(
            Roadmap.user_id == current_user.id,
            func.date(Roadmap.created_at) == date.today()
        ).count()

        if today_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"일일 로드맵 생성 한도를 초과했습니다. (오늘 {today_count}개 생성, 제한: {limit}개)",
            )

    async def event_generator():
        """SSE 이벤트 생성기."""
        try:
            async for event in generate_roadmap_streaming(
                topic=data.topic,
                duration_months=data.duration_months,
                start_date=data.start_date,
                mode=data.mode,
                user_id=str(current_user.id),
                db=db,
                interview_context=data.interview_context,
            ):
                event_type = event["type"]
                event_data = json.dumps(event["data"], ensure_ascii=False, default=str)
                yield f"event: {event_type}\ndata: {event_data}\n\n"
        except Exception as e:
            error_data = json.dumps({
                "message": str(e),
                "recoverable": False
            }, ensure_ascii=False)
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # nginx 버퍼링 비활성화
        }
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


@router.post("/weekly-tasks/{task_id}/generate-daily", response_model=DailyTasksGenerateResponse)
async def generate_daily_tasks_for_week(
    task_id: UUID,
    data: DailyTasksGenerateRequest = DailyTasksGenerateRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크에 대한 일일 태스크 생성 (지연 생성).

    이전 주차가 완료되어야 생성 가능. force=True면 건너뜀.
    첫 주차(1개월차 1주차)는 항상 생성 가능.
    """
    service = DailyGenerationService(db)
    weekly_task = await service.generate_daily_tasks_for_week(
        task_id, current_user.id, force=data.force
    )

    # Count daily tasks
    daily_tasks_count = len(weekly_task.daily_tasks) if weekly_task.daily_tasks else 0

    return DailyTasksGenerateResponse(
        weekly_task_id=str(task_id),
        message="일일 태스크가 성공적으로 생성되었습니다.",
        daily_tasks_count=daily_tasks_count,
    )


@router.get("/weekly-tasks/{task_id}/has-daily-tasks")
async def check_has_daily_tasks(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크에 일일 태스크가 있는지 확인."""
    service = DailyGenerationService(db)
    # Verify ownership
    service.get_weekly_task_with_context(task_id, current_user.id)
    has_tasks = service.has_daily_tasks(task_id)
    return {"has_daily_tasks": has_tasks, "weekly_task_id": str(task_id)}


@router.get("/weekly-tasks/{task_id}/can-generate-daily")
async def check_can_generate_daily(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 태스크의 일일 태스크 생성 가능 여부 확인.

    Returns:
        - can_generate: 생성 가능 여부
        - has_daily_tasks: 이미 일일 태스크가 있는지
        - is_previous_week_completed: 이전 주가 완료되었는지
        - reason: 생성 불가 시 사유
    """
    service = DailyGenerationService(db)
    weekly_task, _ = service.get_weekly_task_with_context(task_id, current_user.id)

    has_tasks = service.has_daily_tasks(task_id)
    is_prev_completed = service.is_previous_week_completed(weekly_task)

    can_generate = not has_tasks and is_prev_completed

    reason = None
    if has_tasks:
        reason = "이미 일일 태스크가 생성되어 있습니다."
    elif not is_prev_completed:
        reason = "이전 주차를 먼저 완료해야 합니다."

    return {
        "weekly_task_id": str(task_id),
        "can_generate": can_generate,
        "has_daily_tasks": has_tasks,
        "is_previous_week_completed": is_prev_completed,
        "reason": reason,
    }


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
