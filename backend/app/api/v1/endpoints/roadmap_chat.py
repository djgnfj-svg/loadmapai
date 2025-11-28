"""
API endpoints for AI-powered roadmap chat editing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.db import get_db
from app.models.user import User
from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask, RoadmapConversation
from app.api.deps import get_current_user
from app.ai.edit_graph import process_edit_request, process_quick_action, QUICK_ACTIONS

router = APIRouter()


# ============ Request/Response Models ============

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[dict] = None  # { target_type, target_id } for focused editing


class ChangeItem(BaseModel):
    id: str
    target_type: str
    target_id: Optional[str] = None
    action: str
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    parent_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    message: str
    changes: List[ChangeItem] = []
    suggestions: List[str] = []


class ApplyChangesRequest(BaseModel):
    change_ids: List[str]
    changes: List[ChangeItem]


class ApplyChangesResponse(BaseModel):
    success: bool
    applied_count: int
    message: str


class ConversationResponse(BaseModel):
    id: UUID
    role: str
    content: str
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    created_at: str

    class Config:
        from_attributes = True


class QuickActionsResponse(BaseModel):
    actions: List[str]


# ============ Helper Functions ============

def get_roadmap_full_context(db: Session, roadmap_id: UUID, user_id: UUID) -> dict:
    """Get roadmap with all nested data for AI context."""
    roadmap = (
        db.query(Roadmap)
        .options(
            joinedload(Roadmap.monthly_goals)
            .joinedload(MonthlyGoal.weekly_tasks)
            .joinedload(WeeklyTask.daily_tasks)
        )
        .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
        .first()
    )

    if not roadmap:
        return None

    # Convert to dict format for AI
    context = {
        "id": str(roadmap.id),
        "title": roadmap.title,
        "topic": roadmap.topic,
        "duration_months": roadmap.duration_months,
        "daily_available_minutes": roadmap.daily_available_minutes,
        "rest_days": roadmap.rest_days or [],
        "intensity": roadmap.intensity,
        "monthly_goals": []
    }

    for monthly in sorted(roadmap.monthly_goals, key=lambda m: m.month_number):
        monthly_data = {
            "id": str(monthly.id),
            "month_number": monthly.month_number,
            "title": monthly.title,
            "description": monthly.description,
            "weekly_tasks": []
        }

        for weekly in sorted(monthly.weekly_tasks, key=lambda w: w.week_number):
            weekly_data = {
                "id": str(weekly.id),
                "week_number": weekly.week_number,
                "title": weekly.title,
                "description": weekly.description,
                "daily_tasks": []
            }

            for daily in sorted(weekly.daily_tasks, key=lambda d: (d.day_number, d.order)):
                daily_data = {
                    "id": str(daily.id),
                    "day_number": daily.day_number,
                    "order": daily.order,
                    "title": daily.title,
                    "description": daily.description,
                }
                weekly_data["daily_tasks"].append(daily_data)

            monthly_data["weekly_tasks"].append(weekly_data)

        context["monthly_goals"].append(monthly_data)

    return context


def save_conversation(
    db: Session,
    roadmap_id: UUID,
    role: str,
    content: str,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    changes_applied: Optional[str] = None,
) -> RoadmapConversation:
    """Save a conversation message."""
    conversation = RoadmapConversation(
        roadmap_id=roadmap_id,
        role=role,
        content=content,
        target_type=target_type,
        target_id=target_id,
        changes_applied=changes_applied,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


# ============ API Endpoints ============

@router.post("/{roadmap_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    roadmap_id: UUID,
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a chat message for AI-powered roadmap editing."""
    # Get roadmap context
    context = get_roadmap_full_context(db, roadmap_id, current_user.id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )

    # Save user message
    save_conversation(
        db=db,
        roadmap_id=roadmap_id,
        role="user",
        content=request.message,
        target_type=request.context.get("target_type") if request.context else None,
        target_id=UUID(request.context["target_id"]) if request.context and request.context.get("target_id") else None,
    )

    # Process with AI
    try:
        result = await process_edit_request(
            user_message=request.message,
            roadmap_context=context,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 처리 중 오류가 발생했습니다: {str(e)}",
        )

    # Save assistant response
    import json
    save_conversation(
        db=db,
        roadmap_id=roadmap_id,
        role="assistant",
        content=result.get("response_message", ""),
        changes_applied=json.dumps(result.get("changes", []), ensure_ascii=False) if result.get("changes") else None,
    )

    return ChatMessageResponse(
        message=result.get("response_message", ""),
        changes=[ChangeItem(**c) for c in result.get("changes", [])],
        suggestions=result.get("suggestions", []),
    )


@router.post("/{roadmap_id}/chat/quick-action", response_model=ChatMessageResponse)
async def send_quick_action(
    roadmap_id: UUID,
    action_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a predefined quick action for roadmap editing."""
    # Get roadmap context
    context = get_roadmap_full_context(db, roadmap_id, current_user.id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )

    # Process quick action
    try:
        result = await process_quick_action(
            action_name=action_name,
            roadmap_context=context,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 처리 중 오류가 발생했습니다: {str(e)}",
        )

    # Save conversation
    import json
    save_conversation(
        db=db,
        roadmap_id=roadmap_id,
        role="user",
        content=f"[빠른 액션] {action_name}",
    )
    save_conversation(
        db=db,
        roadmap_id=roadmap_id,
        role="assistant",
        content=result.get("response_message", ""),
        changes_applied=json.dumps(result.get("changes", []), ensure_ascii=False) if result.get("changes") else None,
    )

    return ChatMessageResponse(
        message=result.get("response_message", ""),
        changes=[ChangeItem(**c) for c in result.get("changes", [])],
        suggestions=result.get("suggestions", []),
    )


@router.post("/{roadmap_id}/chat/apply", response_model=ApplyChangesResponse)
async def apply_chat_changes(
    roadmap_id: UUID,
    request: ApplyChangesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply AI-suggested changes to the roadmap."""
    # Verify ownership
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.user_id == current_user.id,
    ).first()

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )

    applied_count = 0

    for change in request.changes:
        if change.id not in request.change_ids:
            continue

        try:
            if change.action == "modify" and change.target_id:
                # Handle modification
                if change.target_type == "daily":
                    task = db.query(DailyTask).filter(DailyTask.id == UUID(change.target_id)).first()
                    if task and change.field:
                        setattr(task, change.field, change.new_value)
                        applied_count += 1
                elif change.target_type == "weekly":
                    task = db.query(WeeklyTask).filter(WeeklyTask.id == UUID(change.target_id)).first()
                    if task and change.field:
                        setattr(task, change.field, change.new_value)
                        applied_count += 1
                elif change.target_type == "monthly":
                    goal = db.query(MonthlyGoal).filter(MonthlyGoal.id == UUID(change.target_id)).first()
                    if goal and change.field:
                        setattr(goal, change.field, change.new_value)
                        applied_count += 1

            elif change.action == "add" and change.parent_id:
                # Handle addition
                if change.target_type == "daily":
                    weekly = db.query(WeeklyTask).filter(WeeklyTask.id == UUID(change.parent_id)).first()
                    if weekly:
                        # Get next order for this day
                        max_order = db.query(DailyTask).filter(
                            DailyTask.weekly_task_id == weekly.id,
                        ).count()
                        new_task = DailyTask(
                            weekly_task_id=weekly.id,
                            day_number=1,  # Default, should be in change data
                            order=max_order,
                            title=change.new_value or "새 태스크",
                            description="",
                        )
                        db.add(new_task)
                        applied_count += 1

            elif change.action == "delete" and change.target_id:
                # Handle deletion
                if change.target_type == "daily":
                    task = db.query(DailyTask).filter(DailyTask.id == UUID(change.target_id)).first()
                    if task:
                        db.delete(task)
                        applied_count += 1

        except Exception as e:
            # Log error but continue with other changes
            print(f"Error applying change {change.id}: {e}")
            continue

    # Increment edit count if finalized
    if roadmap.is_finalized and applied_count > 0:
        roadmap.edit_count_after_finalize += 1

    db.commit()

    return ApplyChangesResponse(
        success=applied_count > 0,
        applied_count=applied_count,
        message=f"{applied_count}개의 변경사항이 적용되었습니다." if applied_count > 0 else "적용된 변경사항이 없습니다.",
    )


@router.get("/{roadmap_id}/chat/history", response_model=List[ConversationResponse])
async def get_chat_history(
    roadmap_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat history for a roadmap."""
    # Verify ownership
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.user_id == current_user.id,
    ).first()

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )

    conversations = (
        db.query(RoadmapConversation)
        .filter(RoadmapConversation.roadmap_id == roadmap_id)
        .order_by(RoadmapConversation.created_at.asc())
        .limit(limit)
        .all()
    )

    return [
        ConversationResponse(
            id=c.id,
            role=c.role,
            content=c.content,
            target_type=c.target_type,
            target_id=c.target_id,
            created_at=c.created_at.isoformat(),
        )
        for c in conversations
    ]


@router.get("/{roadmap_id}/chat/quick-actions", response_model=QuickActionsResponse)
async def get_quick_actions(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available quick actions."""
    # Verify ownership
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.user_id == current_user.id,
    ).first()

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )

    return QuickActionsResponse(actions=list(QUICK_ACTIONS.keys()))
