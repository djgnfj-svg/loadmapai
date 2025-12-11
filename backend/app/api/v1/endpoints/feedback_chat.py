"""Feedback chat API endpoints for roadmap refinement."""
import asyncio
import uuid
import logging
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta

from app.db import get_db
from app.models.user import User
from app.models import Roadmap, MonthlyGoal, WeeklyTask
from app.models.roadmap import RoadmapMode
from app.api.deps import get_current_user
from app.schemas.feedback import (
    FeedbackStartRequest,
    FeedbackStartResponse,
    FeedbackMessageRequest,
    FeedbackMessageResponse,
    FeedbackFinalizeRequest,
    FeedbackFinalizeResponse,
    RoadmapPreviewData,
    RoadmapModifications,
)
from app.ai.feedback_node import analyze_and_modify_roadmap, apply_modifications
from app.ai.prompts.feedback_prompts import WELCOME_MESSAGE


logger = logging.getLogger(__name__)
router = APIRouter()

# Thread pool for async LLM calls
_executor = ThreadPoolExecutor(max_workers=4)


@dataclass
class FeedbackSession:
    """In-memory feedback session data."""
    session_id: str
    user_id: str
    topic: str
    duration_months: int
    start_date: str
    mode: str
    interview_context: Optional[dict]

    # Current roadmap state (mutable)
    title: str
    description: str
    monthly_goals: List[dict]
    weekly_tasks: List[dict]

    # Chat history
    messages: List[dict] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


# In-memory session storage (use Redis in production)
feedback_sessions: Dict[str, FeedbackSession] = {}


def _cleanup_old_sessions():
    """30분 이상 된 세션 정리."""
    now = datetime.utcnow()
    expired = [
        sid for sid, session in feedback_sessions.items()
        if (now - session.created_at).total_seconds() > 1800  # 30분
    ]
    for sid in expired:
        del feedback_sessions[sid]


@router.post("/start", response_model=FeedbackStartResponse)
async def start_feedback_session(
    data: FeedbackStartRequest,
    current_user: User = Depends(get_current_user),
):
    """피드백 세션을 시작합니다."""
    _cleanup_old_sessions()

    session_id = str(uuid.uuid4())
    rd = data.roadmap_data

    session = FeedbackSession(
        session_id=session_id,
        user_id=str(current_user.id),
        topic=rd.topic,
        duration_months=rd.duration_months,
        start_date=rd.start_date,
        mode=rd.mode,
        interview_context=data.interview_context,
        title=rd.title,
        description=rd.description,
        monthly_goals=[g.model_dump() for g in rd.monthly_goals],
        weekly_tasks=rd.weekly_tasks,
        messages=[],
    )

    feedback_sessions[session_id] = session

    return FeedbackStartResponse(
        session_id=session_id,
        welcome_message=WELCOME_MESSAGE,
    )


@router.post("/{session_id}/message", response_model=FeedbackMessageResponse)
async def send_feedback_message(
    session_id: str,
    data: FeedbackMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """피드백 메시지를 전송하고 AI 응답을 받습니다."""
    session = feedback_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="피드백 세션을 찾을 수 없습니다. 새로 시작해주세요.",
        )

    # 권한 확인
    if session.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    # 사용자 메시지 추가
    session.messages.append({
        "role": "user",
        "content": data.message,
    })

    # 현재 로드맵 데이터 구성
    current_roadmap = {
        "topic": session.topic,
        "duration_months": session.duration_months,
        "start_date": session.start_date,
        "mode": session.mode,
        "title": session.title,
        "description": session.description,
        "monthly_goals": session.monthly_goals,
        "weekly_tasks": session.weekly_tasks,
    }

    try:
        # AI 분석 (비동기로 실행)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            analyze_and_modify_roadmap,
            data.message,
            current_roadmap,
            session.messages,
            session.interview_context,
        )

        # 수정 사항 적용
        modifications = result.get("modifications", {})
        if result.get("modification_type") != "none":
            updated_roadmap = apply_modifications(current_roadmap, modifications)
            # 세션 상태 업데이트
            session.title = updated_roadmap.get("title", session.title)
            session.description = updated_roadmap.get("description", session.description)
            session.monthly_goals = updated_roadmap.get("monthly_goals", session.monthly_goals)
            session.weekly_tasks = updated_roadmap.get("weekly_tasks", session.weekly_tasks)
        else:
            updated_roadmap = current_roadmap

        # AI 응답 추가
        session.messages.append({
            "role": "assistant",
            "content": result.get("response", ""),
        })

        # 응답 구성
        return FeedbackMessageResponse(
            response=result.get("response", ""),
            modifications=RoadmapModifications(
                monthly_goals=modifications.get("monthly_goals"),
                weekly_tasks=modifications.get("weekly_tasks"),
            ) if modifications.get("monthly_goals") or modifications.get("weekly_tasks") else None,
            updated_roadmap=RoadmapPreviewData(
                topic=updated_roadmap["topic"],
                duration_months=updated_roadmap["duration_months"],
                start_date=updated_roadmap["start_date"],
                mode=updated_roadmap["mode"],
                title=updated_roadmap["title"],
                description=updated_roadmap["description"],
                monthly_goals=updated_roadmap["monthly_goals"],
                weekly_tasks=updated_roadmap["weekly_tasks"],
            ),
        )

    except Exception as e:
        logger.error(f"Feedback processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="피드백 처리 중 오류가 발생했습니다.",
        )


@router.post("/{session_id}/finalize", response_model=FeedbackFinalizeResponse)
async def finalize_roadmap(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """로드맵을 확정하고 DB에 저장합니다."""
    session = feedback_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="피드백 세션을 찾을 수 없습니다.",
        )

    if session.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    try:
        # 날짜 파싱
        start = date.fromisoformat(session.start_date)
        end = start + relativedelta(months=session.duration_months)

        # Roadmap 생성
        roadmap = Roadmap(
            user_id=current_user.id,
            title=session.title,
            description=session.description,
            topic=session.topic,
            duration_months=session.duration_months,
            start_date=start,
            end_date=end,
            mode=RoadmapMode(session.mode),
            is_finalized=False,
        )
        db.add(roadmap)
        db.flush()

        # Monthly goals & Weekly tasks 저장
        for monthly_data in session.monthly_goals:
            monthly_goal = MonthlyGoal(
                roadmap_id=roadmap.id,
                month_number=monthly_data["month_number"],
                title=monthly_data["title"],
                description=monthly_data["description"],
            )
            db.add(monthly_goal)
            db.flush()

            # 해당 월의 주간 과제 찾기
            weekly_month = next(
                (w for w in session.weekly_tasks
                 if w.get("month_number") == monthly_data["month_number"]),
                None
            )

            if weekly_month and "weeks" in weekly_month:
                for week_data in weekly_month["weeks"]:
                    weekly_task = WeeklyTask(
                        monthly_goal_id=monthly_goal.id,
                        week_number=week_data["week_number"],
                        title=week_data["title"],
                        description=week_data["description"],
                    )
                    db.add(weekly_task)

        db.commit()

        roadmap_id = str(roadmap.id)

        # 세션 정리
        del feedback_sessions[session_id]

        return FeedbackFinalizeResponse(
            roadmap_id=roadmap_id,
            title=session.title,
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to finalize roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로드맵 저장 중 오류가 발생했습니다.",
        )


@router.delete("/{session_id}")
async def cancel_feedback_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """피드백 세션을 취소합니다."""
    session = feedback_sessions.get(session_id)
    if not session:
        return {"message": "세션이 이미 종료되었습니다."}

    if session.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    del feedback_sessions[session_id]
    return {"message": "세션이 취소되었습니다."}


async def _generate_first_week_daily_tasks(
    roadmap_id: str,
    user_id: str,
    db: Session,
    interview_context: dict = None,
):
    """첫 주의 일일 태스크를 생성합니다."""
    from uuid import UUID
    from app.services.daily_generation_service import DailyGenerationService

    first_week = (
        db.query(WeeklyTask)
        .join(MonthlyGoal)
        .filter(
            MonthlyGoal.roadmap_id == UUID(roadmap_id),
            MonthlyGoal.month_number == 1,
            WeeklyTask.week_number == 1,
        )
        .first()
    )

    if first_week:
        service = DailyGenerationService(db)
        await service.generate_daily_tasks_for_week(
            first_week.id,
            UUID(user_id),
            force=True,
            interview_context=interview_context,
        )
