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
            status=InterviewStatus.IN_PROGRESS,
            # Multi-round tracking
            current_round=1,
            max_rounds=3,
            all_questions=[],
            all_answers=[],
            evaluations=[],
            invalid_history=[],
            invalid_count=0,
            consecutive_invalid=0,
            is_terminated=False,
            # Current round data
            current_questions=[],
            current_answers=[],
            current_evaluations=[],
            # Legacy
            current_stage=1,
            stage_data={},
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
        # Update multi-round tracking
        session.current_round = state.get("current_round", session.current_round)
        session.max_rounds = state.get("max_rounds", session.max_rounds)

        # Update all questions and answers
        session.all_questions = state.get("all_questions", session.all_questions or [])
        session.all_answers = state.get("all_answers", session.all_answers or [])
        session.evaluations = state.get("evaluations", session.evaluations or [])

        # Update invalid tracking
        session.invalid_history = state.get("invalid_history", session.invalid_history or [])
        session.invalid_count = state.get("invalid_count", session.invalid_count or 0)
        session.consecutive_invalid = state.get("consecutive_invalid", session.consecutive_invalid or 0)

        # Update termination status
        session.is_terminated = state.get("is_terminated", False)
        session.termination_reason = state.get("termination_reason")
        session.warning_message = state.get("warning_message")

        # Update current working state
        session.current_questions = state.get("current_questions", [])
        session.current_answers = state.get("current_answers", [])
        session.current_evaluations = state.get("current_evaluations", [])

        # Legacy fields
        session.current_stage = state.get("current_stage", session.current_stage)
        if state.get("stage_data"):
            session.stage_data = {
                str(k): v for k, v in state["stage_data"].items()
            }
        session.followup_count = state.get("followup_count", 0)
        session.pending_followup_questions = state.get("pending_followup_questions", [])

        # Update completion/termination status
        if state.get("is_terminated") and not state.get("is_complete"):
            session.status = InterviewStatus.TERMINATED
        elif state.get("is_complete"):
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
            # Multi-round tracking
            "current_round": session.current_round or 1,
            "max_rounds": session.max_rounds or 3,
            "all_questions": session.all_questions or [],
            "all_answers": session.all_answers or [],
            "evaluations": session.evaluations or [],
            "invalid_history": session.invalid_history or [],
            "invalid_count": session.invalid_count or 0,
            "consecutive_invalid": session.consecutive_invalid or 0,
            "is_terminated": session.is_terminated or False,
            "termination_reason": session.termination_reason,
            "warning_message": session.warning_message,
            # Current round data
            "current_questions": session.current_questions or [],
            "current_answers": session.current_answers or [],
            "current_evaluations": session.current_evaluations or [],
            # Legacy fields
            "current_stage": session.current_stage,
            "stages_completed": list(stage_data.keys()) if stage_data else [],
            "max_followups_per_stage": session.max_followups_per_stage,
            "stage_data": stage_data,
            "followup_count": session.followup_count,
            "pending_followup_questions": session.pending_followup_questions or [],
            # Completion data
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
