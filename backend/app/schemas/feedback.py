"""Feedback chat schemas for roadmap refinement."""
from typing import List, Optional, Literal, Any
from datetime import date
from pydantic import BaseModel, Field


class MonthlyGoalData(BaseModel):
    """월별 목표 데이터."""
    month_number: int
    title: str
    description: str


class WeeklyTaskData(BaseModel):
    """주간 과제 데이터."""
    month_number: int
    week_number: int
    title: str
    description: str


class RoadmapPreviewData(BaseModel):
    """로드맵 프리뷰 데이터 (DB 저장 전 상태)."""
    topic: str
    duration_months: int = Field(..., ge=1, le=6)
    start_date: str  # YYYY-MM-DD format
    mode: str  # PLANNING or LEARNING
    title: str
    description: str
    monthly_goals: List[MonthlyGoalData]
    weekly_tasks: List[dict]  # [{month_number, weeks: [...]}]


class RoadmapModifications(BaseModel):
    """AI가 수정한 항목들."""
    monthly_goals: Optional[List[MonthlyGoalData]] = None
    weekly_tasks: Optional[List[WeeklyTaskData]] = None


class FeedbackMessage(BaseModel):
    """채팅 메시지."""
    role: Literal["user", "assistant"]
    content: str


# Request schemas
class FeedbackStartRequest(BaseModel):
    """피드백 세션 시작 요청."""
    roadmap_data: RoadmapPreviewData
    interview_context: Optional[dict] = None


class FeedbackMessageRequest(BaseModel):
    """피드백 메시지 전송 요청."""
    message: str = Field(..., min_length=1, max_length=2000)


class FeedbackFinalizeRequest(BaseModel):
    """로드맵 확정 요청."""
    roadmap_data: RoadmapPreviewData


# Response schemas
class FeedbackStartResponse(BaseModel):
    """피드백 세션 시작 응답."""
    session_id: str
    welcome_message: str


class FeedbackMessageResponse(BaseModel):
    """피드백 메시지 응답."""
    response: str  # AI 응답 메시지
    modifications: Optional[RoadmapModifications] = None
    updated_roadmap: RoadmapPreviewData


class FeedbackFinalizeResponse(BaseModel):
    """로드맵 확정 응답."""
    roadmap_id: str
    title: str
