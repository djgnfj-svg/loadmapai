import uuid
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식
    SHORT_ANSWER = "short_answer"        # 단답형
    ESSAY = "essay"                      # 서술형


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)

    # Question details
    question_number = Column(Integer, nullable=False)  # Order in quiz (1-indexed)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)

    # For multiple choice questions
    options = Column(JSONB, nullable=True)  # ["option1", "option2", "option3", "option4"]

    # Correct answer (for grading reference)
    correct_answer = Column(Text, nullable=True)  # For multiple_choice: "A", "B", etc.
    explanation = Column(Text, nullable=True)     # Why this is the correct answer

    # Point value
    points = Column(Integer, default=10, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    user_answer = relationship("UserAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question {self.question_number} - {self.question_type}>"
