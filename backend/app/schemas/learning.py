from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.question import QuestionType


# Question schemas
class QuestionBase(BaseModel):
    question_type: QuestionType
    question_text: str
    choices: Optional[List[str]] = None  # 객관식만 해당
    hint: Optional[str] = None


class QuestionCreate(QuestionBase):
    correct_answer: str
    explanation: Optional[str] = None
    order: int = Field(default=0, ge=0)


class QuestionResponse(QuestionBase):
    id: UUID
    daily_task_id: UUID
    order: int
    user_answer: Optional["UserAnswerResponse"] = None

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    """채점 후 정답 포함 응답"""
    correct_answer: str
    explanation: Optional[str] = None


# UserAnswer schemas
class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)


class UserAnswerResponse(BaseModel):
    id: UUID
    question_id: UUID
    answer_text: str
    is_correct: Optional[bool] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionResultResponse(BaseModel):
    """개별 문제 채점 결과"""
    question_id: UUID
    question_type: QuestionType
    question_text: str
    your_answer: str
    correct_answer: str
    is_correct: bool
    score: Optional[int] = None  # 서술형만
    feedback: str
    explanation: Optional[str] = None


# DailyFeedback schemas
class DailyFeedbackResponse(BaseModel):
    id: UUID
    weekly_task_id: UUID
    day_number: int
    total_questions: int
    correct_count: int
    accuracy_rate: float  # 0.0 ~ 1.0
    is_passed: bool  # 70% 이상 여부
    summary: str
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    question_results: Optional[List[QuestionResultResponse]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompleteDayResponse(BaseModel):
    """일일 학습 완료 응답"""
    feedback: DailyFeedbackResponse
    next_day_available: bool  # 다음 일차 진행 가능 여부
    week_completed: bool  # 주간 완료 여부


# Wrong questions & Review
class WrongQuestionResponse(BaseModel):
    """틀린 문제 정보"""
    question: QuestionWithAnswer
    your_answer: str
    day_number: int


class ReviewSessionResponse(BaseModel):
    """복습 세션 정보"""
    daily_task_id: UUID
    total_questions: int
    questions: List[QuestionResponse]


# Learning mode daily task info
class LearningDayInfoResponse(BaseModel):
    """러닝 모드 일일 정보"""
    daily_task_id: UUID
    weekly_task_id: UUID
    day_number: int
    title: str
    description: Optional[str] = None
    total_questions: int
    answered_count: int
    is_completed: bool
    feedback: Optional[DailyFeedbackResponse] = None


class LearningWeekInfoResponse(BaseModel):
    """러닝 모드 주간 정보"""
    weekly_task_id: UUID
    week_number: int
    title: str
    description: Optional[str] = None
    days: List[LearningDayInfoResponse]
    total_questions: int
    correct_count: int
    accuracy_rate: float
    is_completed: bool
    review_available: bool  # 틀린 문제 복습 가능 여부


# Forward references 해결
QuestionResponse.model_rebuild()
