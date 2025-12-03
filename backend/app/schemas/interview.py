"""Interview schemas for SMART-based goal setting."""
from typing import List, Optional, Union, Literal, Any
from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """A single interview question."""
    id: str
    category: Literal["specific", "measurable", "achievable", "relevant"]
    question: str
    type: Literal["text", "select", "multiselect"]
    options: Optional[List[str]] = None


class InterviewAnswer(BaseModel):
    """Answer to an interview question."""
    question_id: str
    answer: Union[str, List[str]]


class InterviewContext(BaseModel):
    """Structured context extracted from interview answers."""
    specific_goal: str
    expected_outcome: str
    measurement_criteria: str
    current_level: str
    available_resources: dict[str, Any]
    motivation: str
    challenges: List[str]


# Request/Response schemas
class InterviewStartRequest(BaseModel):
    """Request to start an interview session."""
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)


class InterviewStartResponse(BaseModel):
    """Response with initial interview questions."""
    session_id: str
    questions: List[InterviewQuestion]
    round: int = 1


class InterviewSubmitRequest(BaseModel):
    """Request to submit interview answers."""
    session_id: str
    answers: List[InterviewAnswer]


class InterviewSubmitResponse(BaseModel):
    """Response after submitting answers."""
    status: Literal["completed", "followup_needed"]
    round: int
    followup_questions: Optional[List[InterviewQuestion]] = None
    interview_context: Optional[InterviewContext] = None
