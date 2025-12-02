import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MonthlyGoal(Base, TimestampMixin):
    __tablename__ = "monthly_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)

    month_number = Column(Integer, nullable=False)  # 1, 2, 3, ...
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]), default=TaskStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100

    # Relationships
    roadmap = relationship("Roadmap", back_populates="monthly_goals")
    weekly_tasks = relationship(
        "WeeklyTask",
        back_populates="monthly_goal",
        cascade="all, delete-orphan",
        order_by="WeeklyTask.week_number"
    )

    def __repr__(self):
        return f"<MonthlyGoal {self.month_number}: {self.title}>"
