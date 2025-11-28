import uuid
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class QuizStatus(str, Enum):
    PENDING = "pending"       # Generated but not started
    IN_PROGRESS = "in_progress"  # User is taking the quiz
    COMPLETED = "completed"   # User submitted all answers
    GRADED = "graded"        # AI graded the quiz


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daily_task_id = Column(UUID(as_uuid=True), ForeignKey("daily_tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status = Column(SQLEnum(QuizStatus), default=QuizStatus.PENDING, nullable=False)

    # Quiz metadata
    total_questions = Column(Integer, default=0, nullable=False)

    # Grading results (populated after grading)
    score = Column(Float, nullable=True)  # 0-100
    correct_count = Column(Integer, nullable=True)
    feedback_summary = Column(Text, nullable=True)  # AI-generated overall feedback

    # Relationships
    daily_task = relationship("DailyTask", backref="quizzes")
    user = relationship("User", backref="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.id} - {self.status}>"
