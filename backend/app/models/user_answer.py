import uuid
from sqlalchemy import Column, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 사용자 답변
    answer_text = Column(Text, nullable=False)

    # 채점 결과 (null = 미채점)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Integer, nullable=True)  # 0-100 (서술형용)

    # AI 피드백
    feedback = Column(Text, nullable=True)

    # 제출/채점 시간
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    graded_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    question = relationship("Question", back_populates="user_answer")
    user = relationship("User", backref="user_answers")

    def __repr__(self):
        return f"<UserAnswer question_id={self.question_id} is_correct={self.is_correct}>"
