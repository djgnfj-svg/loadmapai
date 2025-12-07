import uuid
import enum
from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class QuestionType(str, enum.Enum):
    ESSAY = "ESSAY"  # 서술형
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"  # 객관식
    SHORT_ANSWER = "SHORT_ANSWER"  # 단답식


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daily_task_id = Column(UUID(as_uuid=True), ForeignKey("daily_tasks.id", ondelete="CASCADE"), nullable=False)

    # 문제 내용
    question_type = Column(SQLEnum(QuestionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    question_text = Column(Text, nullable=False)

    # 객관식 전용: ["선택지1", "선택지2", "선택지3", "선택지4"]
    choices = Column(JSONB, nullable=True)

    # 정답: 객관식은 인덱스("0", "1" 등), 서술형/단답식은 모범답안
    correct_answer = Column(Text, nullable=False)

    # 힌트 및 해설
    hint = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    # 같은 일자 내 문제 순서
    order = Column(Integer, default=0, nullable=False)

    # Relationships
    daily_task = relationship("DailyTask", back_populates="questions")
    user_answer = relationship("UserAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question {self.order}: {self.question_type.value}>"
