from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
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
    DailyTaskResponse,
)
from app.services.roadmap_service import RoadmapService, DailyTaskService
from app.api.deps import get_current_user
from app.ai.roadmap_graph import generate_roadmap


class RoadmapGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    mode: RoadmapMode = RoadmapMode.PLANNING


class RoadmapGenerateResponse(BaseModel):
    roadmap_id: str
    title: str
    message: str

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
