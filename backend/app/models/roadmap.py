import uuid
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class RoadmapMode(str, enum.Enum):
    PLANNING = "planning"  # 플래닝 모드 - 체크리스트 중심
    LEARNING = "learning"  # 러닝 모드 - 퀴즈/학습 중심


class RoadmapStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class Roadmap(Base, TimestampMixin):
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String(200), nullable=False)  # 학습 주제

    # Duration: 1-6 months
    duration_months = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Mode and status
    mode = Column(SQLEnum(RoadmapMode), default=RoadmapMode.PLANNING, nullable=False)
    status = Column(SQLEnum(RoadmapStatus), default=RoadmapStatus.ACTIVE, nullable=False)

    # Progress (0-100)
    progress = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", backref="roadmaps")
    monthly_goals = relationship("MonthlyGoal", back_populates="roadmap", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Roadmap {self.title}>"
