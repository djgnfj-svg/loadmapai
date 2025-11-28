from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.quiz import QuizStatus
from app.models.question import QuestionType


# ============ Question Schemas ============

class QuestionBase(BaseModel):
    question_type: QuestionType
    question_text: str
    options: Optional[List[str]] = None  # For multiple choice
    points: int = 10


class QuestionCreate(QuestionBase):
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: UUID
    question_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    """Question with correct answer revealed (for review)"""
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


# ============ User Answer Schemas ============

class UserAnswerBase(BaseModel):
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None  # For multiple choice


class UserAnswerCreate(UserAnswerBase):
    question_id: UUID


class UserAnswerResponse(UserAnswerBase):
    id: UUID
    question_id: UUID
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer for a question"""
    question_id: UUID  # 필수: 어느 문제에 대한 답변인지 식별
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None


# ============ Quiz Schemas ============

class QuizBase(BaseModel):
    daily_task_id: UUID


class QuizCreate(QuizBase):
    pass


class QuizResponse(BaseModel):
    id: UUID
    daily_task_id: UUID
    status: QuizStatus
    total_questions: int
    score: Optional[float] = None
    correct_count: Optional[int] = None
    feedback_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizWithQuestions(QuizResponse):
    """Quiz with all questions (without answers for taking quiz)"""
    questions: List[QuestionResponse] = []


class QuizDetail(QuizResponse):
    """Quiz with questions and user answers (for review)"""
    questions: List[QuestionWithAnswer] = []
    user_answers: List[UserAnswerResponse] = []


class QuizResult(BaseModel):
    """Quiz result after grading"""
    quiz_id: UUID
    status: QuizStatus
    total_questions: int
    correct_count: int
    score: float
    feedback_summary: str
    questions: List[QuestionWithAnswer] = []
    user_answers: List[UserAnswerResponse] = []


# ============ Quiz Generation Request ============

class QuizGenerateRequest(BaseModel):
    """Request to generate a quiz for a daily task"""
    daily_task_id: UUID
    num_questions: int = Field(default=5, ge=5, le=10)


class QuizGenerateResponse(BaseModel):
    """Response after generating a quiz"""
    quiz_id: UUID
    message: str


# ============ Quiz Submit Request ============

class QuizSubmitRequest(BaseModel):
    """Request to submit all answers and complete the quiz"""
    answers: List[SubmitAnswerRequest]


class QuizSubmitResponse(BaseModel):
    """Response after submitting quiz (before grading)"""
    quiz_id: UUID
    message: str
    status: QuizStatus
