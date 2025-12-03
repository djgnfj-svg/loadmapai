import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class DailyGoal(Base, TimestampMixin):
    """Daily goal - represents the objective for a specific day within a week."""
    __tablename__ = "daily_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weekly_task_id = Column(UUID(as_uuid=True), ForeignKey("weekly_tasks.id", ondelete="CASCADE"), nullable=False)

    day_number = Column(Integer, nullable=False)  # 1-7
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    weekly_task = relationship("WeeklyTask", back_populates="daily_goals")

    def __repr__(self):
        return f"<DailyGoal Day {self.day_number}: {self.title}>"
