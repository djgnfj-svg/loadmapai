"""Interview session model for deep interview system."""
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class InterviewStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"  # 인터뷰 진행 중
    COMPLETED = "completed"  # 인터뷰 완료
    ABANDONED = "abandoned"  # 인터뷰 포기


class InterviewSession(Base, TimestampMixin):
    """Stores multi-stage deep interview sessions.

    The interview consists of 3 stages:
    1. Goal Clarification - What do you want to achieve?
    2. Current State - What do you already know?
    3. Constraints - Time, resources, limitations
    """
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Interview parameters
    topic = Column(String(200), nullable=False)
    mode = Column(String(20), nullable=False)  # "learning" or "planning"
    duration_months = Column(Integer, nullable=False)

    # Stage tracking
    current_stage = Column(Integer, default=1, nullable=False)  # 1, 2, or 3
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.IN_PROGRESS, nullable=False)

    # Stage data (JSON blob storing all Q&A per stage)
    # Format: {
    #   "1": {"questions": [...], "answers": [...], "evaluations": [...], ...},
    #   "2": {...},
    #   "3": {...}
    # }
    stage_data = Column(JSONB, default={}, nullable=False)

    # Current stage working data
    current_questions = Column(JSONB, default=[], nullable=False)
    current_answers = Column(JSONB, default=[], nullable=False)
    current_evaluations = Column(JSONB, default=[], nullable=False)

    # Follow-up tracking
    followup_count = Column(Integer, default=0, nullable=False)
    pending_followup_questions = Column(JSONB, default=[], nullable=False)
    max_followups_per_stage = Column(Integer, default=2, nullable=False)

    # Compiled results (populated after completion)
    compiled_context = Column(Text, nullable=True)
    key_insights = Column(JSONB, default=[], nullable=True)

    # Extracted schedule from Stage 3
    extracted_daily_minutes = Column(Integer, nullable=True)
    extracted_rest_days = Column(JSONB, nullable=True)  # List of day numbers [0-6]
    extracted_intensity = Column(String(20), nullable=True)  # light/moderate/intense

    # Link to generated roadmap (if any)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", backref="interview_sessions")
    roadmap = relationship("Roadmap", backref="interview_session")

    def __repr__(self):
        return f"<InterviewSession {self.id} - {self.topic}>"

    @property
    def is_complete(self) -> bool:
        return self.status == InterviewStatus.COMPLETED

    @property
    def stages_completed(self) -> list:
        """Get list of completed stage numbers."""
        return [int(k) for k in self.stage_data.keys() if k.isdigit()]
