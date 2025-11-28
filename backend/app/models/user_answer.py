import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # User's response
    answer_text = Column(Text, nullable=True)  # User's answer
    selected_option = Column(String(10), nullable=True)  # For multiple choice: "A", "B", etc.

    # Grading results (populated after AI grading)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)  # 0-100 for partial credit (essay)
    feedback = Column(Text, nullable=True)  # AI-generated feedback for this answer

    # Relationships
    question = relationship("Question", back_populates="user_answer")
    user = relationship("User", backref="answers")

    def __repr__(self):
        return f"<UserAnswer for Question {self.question_id}>"
