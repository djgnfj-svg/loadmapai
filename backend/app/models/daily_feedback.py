import uuid
from sqlalchemy import Column, Boolean, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class DailyFeedback(Base, TimestampMixin):
    __tablename__ = "daily_feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weekly_task_id = Column(UUID(as_uuid=True), ForeignKey("weekly_tasks.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1-7
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 결과 요약
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    accuracy_rate = Column(Float, nullable=False)  # 0.0 ~ 1.0

    # 합격 여부 (70% 이상)
    is_passed = Column(Boolean, nullable=False)

    # AI 생성 피드백
    summary = Column(Text, nullable=False)
    strengths = Column(JSONB, nullable=True)  # ["잘한 점1", "잘한 점2"]
    improvements = Column(JSONB, nullable=True)  # ["개선점1", "개선점2"]

    # Relationships
    weekly_task = relationship("WeeklyTask", backref="daily_feedbacks")
    user = relationship("User", backref="daily_feedbacks")

    def __repr__(self):
        return f"<DailyFeedback day={self.day_number} accuracy={self.accuracy_rate:.0%}>"
