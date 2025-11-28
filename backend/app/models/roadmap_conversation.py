import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class RoadmapConversation(Base, TimestampMixin):
    """AI 대화 수정 기록을 저장하는 모델"""
    __tablename__ = "roadmap_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)

    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)

    # 타겟 정보 (특정 항목에 대한 대화인 경우)
    target_type = Column(String(20), nullable=True)  # "monthly" | "weekly" | "daily"
    target_id = Column(UUID(as_uuid=True), nullable=True)

    # 적용된 변경사항 (JSON 형태)
    changes_applied = Column(Text, nullable=True)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="conversations")

    def __repr__(self):
        return f"<RoadmapConversation {self.role}: {self.content[:50]}...>"
