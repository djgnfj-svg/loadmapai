"""Service layer for interview session management."""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.interview_session import InterviewSession, InterviewStatus
from app.schemas.interview import (
    InterviewStageInfo,
    InterviewQuestionSchema,
    InterviewAnswerSchema,
    get_stage_name,
)


class InterviewService:
    """Service for managing interview sessions."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        user_id: UUID,
        topic: str,
        mode: str,
        duration_months: int,
    ) -> InterviewSession:
        """Create a new interview session."""
        session = InterviewSession(
            user_id=user_id,
            topic=topic,
            mode=mode,
            duration_months=duration_months,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={},
            current_questions=[],
            current_answers=[],
            current_evaluations=[],
            followup_count=0,
            pending_followup_questions=[],
            max_followups_per_stage=2,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: UUID, user_id: UUID) -> Optional[InterviewSession]:
        """Get an interview session by ID."""
        return self.db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        ).first()

    def get_sessions_for_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[InterviewStatus] = None,
    ) -> List[InterviewSession]:
        """Get all interview sessions for a user."""
        query = self.db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        )
        if status:
            query = query.filter(InterviewSession.status == status)
        return query.order_by(InterviewSession.created_at.desc()).offset(skip).limit(limit).all()

    def count_sessions_for_user(
        self,
        user_id: UUID,
        status: Optional[InterviewStatus] = None,
    ) -> int:
        """Count interview sessions for a user."""
        query = self.db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        )
        if status:
            query = query.filter(InterviewSession.status == status)
        return query.count()

    def update_session_state(
        self,
        session: InterviewSession,
        state: Dict[str, Any],
    ) -> InterviewSession:
        """Update session with new state from interview graph."""
        # Update stage tracking
        session.current_stage = state.get("current_stage", session.current_stage)

        # Update stage data
        if state.get("stage_data"):
            # Convert integer keys to strings for JSON storage
            session.stage_data = {
                str(k): v for k, v in state["stage_data"].items()
            }

        # Update current working state
        session.current_questions = state.get("current_questions", [])
        session.current_answers = state.get("current_answers", [])
        session.current_evaluations = state.get("current_evaluations", [])

        # Update follow-up tracking
        session.followup_count = state.get("followup_count", 0)
        session.pending_followup_questions = state.get("pending_followup_questions", [])

        # Update completion status
        if state.get("is_complete"):
            session.status = InterviewStatus.COMPLETED
            session.compiled_context = state.get("compiled_context")
            session.key_insights = state.get("key_insights", [])
            session.extracted_daily_minutes = state.get("extracted_daily_minutes")
            session.extracted_rest_days = state.get("extracted_rest_days")
            session.extracted_intensity = state.get("extracted_intensity")

        self.db.commit()
        self.db.refresh(session)
        return session

    def link_roadmap(
        self,
        session_id: UUID,
        roadmap_id: UUID,
        user_id: UUID,
    ) -> Optional[InterviewSession]:
        """Link a generated roadmap to an interview session."""
        session = self.get_session(session_id, user_id)
        if not session:
            return None
        session.roadmap_id = roadmap_id
        self.db.commit()
        self.db.refresh(session)
        return session

    def abandon_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> Optional[InterviewSession]:
        """Mark a session as abandoned."""
        session = self.get_session(session_id, user_id)
        if not session:
            return None
        session.status = InterviewStatus.ABANDONED
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_stages_info(self, session: InterviewSession) -> List[InterviewStageInfo]:
        """Get info about all stages for a session."""
        stages_info = []
        for stage_num in [1, 2, 3]:
            stage_key = str(stage_num)
            stage_data = session.stage_data.get(stage_key, {})
            stages_info.append(InterviewStageInfo(
                stage=stage_num,
                questions_count=len(stage_data.get("questions", [])),
                answers_count=len(stage_data.get("answers", [])),
                completed=bool(stage_data.get("questions")),
            ))
        return stages_info

    def session_to_state(self, session: InterviewSession) -> Dict[str, Any]:
        """Convert DB session to interview graph state."""
        # Convert string keys back to integers for state
        stage_data = {}
        for k, v in (session.stage_data or {}).items():
            try:
                stage_data[int(k)] = v
            except (ValueError, TypeError):
                stage_data[k] = v

        return {
            "session_id": str(session.id),
            "topic": session.topic,
            "mode": session.mode,
            "duration_months": session.duration_months,
            "user_id": str(session.user_id),
            "current_stage": session.current_stage,
            "stages_completed": list(stage_data.keys()) if stage_data else [],
            "max_followups_per_stage": session.max_followups_per_stage,
            "stage_data": stage_data,
            "current_questions": session.current_questions or [],
            "current_answers": session.current_answers or [],
            "current_evaluations": session.current_evaluations or [],
            "followup_count": session.followup_count,
            "pending_followup_questions": session.pending_followup_questions or [],
            "is_complete": session.status == InterviewStatus.COMPLETED,
            "compiled_context": session.compiled_context,
            "key_insights": session.key_insights or [],
            "extracted_daily_minutes": session.extracted_daily_minutes,
            "extracted_rest_days": session.extracted_rest_days,
            "extracted_intensity": session.extracted_intensity,
            "error_message": None,
        }

    def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete an interview session."""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True
