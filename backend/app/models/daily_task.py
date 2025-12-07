import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.models.monthly_goal import TaskStatus


class DailyTask(Base, TimestampMixin):
    __tablename__ = "daily_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weekly_task_id = Column(UUID(as_uuid=True), ForeignKey("weekly_tasks.id", ondelete="CASCADE"), nullable=False)

    day_number = Column(Integer, nullable=False)  # 1-7
    order = Column(Integer, default=0, nullable=False)  # 같은 day_number 내 순서 (다중 태스크 지원)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]), default=TaskStatus.PENDING, nullable=False)
    is_checked = Column(Boolean, default=False, nullable=False)

    # LEARNING 모드 전용 필드
    is_review_task = Column(Boolean, default=False, nullable=False)  # 틀린 문제 복습용
    review_source_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # 복습 대상 원본 문제 IDs

    # Relationships
    weekly_task = relationship("WeeklyTask", back_populates="daily_tasks")
    questions = relationship(
        "Question",
        back_populates="daily_task",
        cascade="all, delete-orphan",
        order_by="Question.order"
    )

    def __repr__(self):
        return f"<DailyTask Day {self.day_number}: {self.title}>"
