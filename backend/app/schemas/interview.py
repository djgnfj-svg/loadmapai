"""Schemas for deep interview API."""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.interview_session import InterviewStatus


# ============ Question Schemas ============

class InterviewQuestionSchema(BaseModel):
    """Single interview question."""
    id: str
    question: str
    question_type: Literal["text", "single_choice", "multiple_choice"]
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None


class InterviewAnswerSchema(BaseModel):
    """Single answer to an interview question."""
    question_id: str
    answer: str


# ============ Request Schemas ============

class InterviewStartRequest(BaseModel):
    """Request to start a new interview session."""
    topic: str = Field(..., min_length=1, max_length=200)
    mode: Literal["learning", "planning"] = "learning"
    duration_months: int = Field(..., ge=1, le=6)


class InterviewSubmitAnswersRequest(BaseModel):
    """Request to submit answers for current questions."""
    answers: List[InterviewAnswerSchema]
    user_wants_complete: bool = False  # 사용자가 "이 정도면 됐어요" 버튼 클릭


# ============ Response Schemas ============

class InterviewStageInfo(BaseModel):
    """Info about a single interview stage."""
    stage: int
    questions_count: int
    answers_count: int
    completed: bool


class InterviewQuestionsResponse(BaseModel):
    """Response containing questions for the user to answer."""
    session_id: UUID
    current_stage: int
    stage_name: str
    questions: List[InterviewQuestionSchema]
    is_complete: bool = False
    is_followup: bool = False

    class Config:
        from_attributes = True


class InterviewAnswerEvaluationSchema(BaseModel):
    """Evaluation result for a single answer."""
    question_id: str
    specificity: float = Field(..., ge=0, le=1)
    relevance: float = Field(..., ge=0, le=1)
    completeness: float = Field(..., ge=0, le=1)
    average_score: float = Field(..., ge=0, le=1)
    needs_followup: bool


class InterviewScheduleSchema(BaseModel):
    """Extracted schedule from interview."""
    daily_minutes: Optional[int] = None
    rest_days: Optional[List[int]] = None
    intensity: Optional[Literal["light", "moderate", "intense"]] = None


class InterviewCompletedResponse(BaseModel):
    """Response when interview is completed."""
    session_id: UUID
    is_complete: bool = True
    compiled_context: str
    key_insights: List[str]
    schedule: InterviewScheduleSchema
    can_generate_roadmap: bool = True


class InterviewSessionResponse(BaseModel):
    """Full interview session response."""
    id: UUID
    user_id: UUID
    topic: str
    mode: str
    duration_months: int
    current_stage: int
    status: InterviewStatus
    stages: List[InterviewStageInfo]
    is_complete: bool
    created_at: datetime
    updated_at: datetime
    roadmap_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class InterviewSessionListResponse(BaseModel):
    """List of interview sessions."""
    sessions: List[InterviewSessionResponse]
    total: int


# ============ Generate Roadmap Request ============

class GenerateRoadmapFromInterviewRequest(BaseModel):
    """Request to generate roadmap from completed interview."""
    session_id: UUID
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


# ============ Stage Name Helper ============

STAGE_NAMES = {
    1: "목표 구체화",
    2: "현재 상태 파악",
    3: "제약 조건",
}


def get_stage_name(stage: int) -> str:
    """Get human-readable stage name."""
    return STAGE_NAMES.get(stage, f"Stage {stage}")
