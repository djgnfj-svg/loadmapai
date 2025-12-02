import uuid
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum as SQLEnum, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class RoadmapMode(str, enum.Enum):
    PLANNING = "planning"  # 플래닝 모드 - 체크리스트 중심


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

    # Finalization (확정 관련)
    is_finalized = Column(Boolean, default=False, nullable=False)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    edit_count_after_finalize = Column(Integer, default=0, nullable=False)

    # User schedule (사용자 스케줄 - AI 로드맵 생성에 활용)
    daily_available_minutes = Column(Integer, default=60)  # 하루 투자 가능 시간 (분)
    rest_days = Column(ARRAY(Integer), default=[])  # 쉬는 요일 [0=일, 1=월, ..., 6=토]
    intensity = Column(String(20), default='moderate')  # 학습 강도: light/moderate/intense

    # Relationships
    user = relationship("User", backref="roadmaps")
    monthly_goals = relationship(
        "MonthlyGoal",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="MonthlyGoal.month_number"
    )

    def __repr__(self):
        return f"<Roadmap {self.title}>"
