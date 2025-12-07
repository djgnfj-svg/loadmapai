import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.models.monthly_goal import TaskStatus


class WeeklyTask(Base, TimestampMixin):
    __tablename__ = "weekly_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monthly_goal_id = Column(UUID(as_uuid=True), ForeignKey("monthly_goals.id", ondelete="CASCADE"), nullable=False)

    week_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]), default=TaskStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100

    # LEARNING 모드 전용 필드
    review_generated = Column(Boolean, default=False, nullable=False)  # 복습 세션 생성 여부

    # Relationships
    monthly_goal = relationship("MonthlyGoal", back_populates="weekly_tasks")
    daily_goals = relationship(
        "DailyGoal",
        back_populates="weekly_task",
        cascade="all, delete-orphan",
        order_by="DailyGoal.day_number"
    )
    daily_tasks = relationship(
        "DailyTask",
        back_populates="weekly_task",
        cascade="all, delete-orphan",
        order_by="DailyTask.day_number, DailyTask.order"
    )

    def __repr__(self):
        return f"<WeeklyTask Week {self.week_number}: {self.title}>"
