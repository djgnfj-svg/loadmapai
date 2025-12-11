from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date, datetime
from uuid import UUID

from app.models.roadmap import RoadmapMode, RoadmapStatus
from app.models.monthly_goal import TaskStatus
from app.models.weekly_task import DailyGenerationStatus


# Daily Goal schemas
class DailyGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class DailyGoalResponse(DailyGoalBase):
    id: UUID
    weekly_task_id: UUID
    day_number: int
    created_at: datetime

    class Config:
        from_attributes = True


# Daily Task schemas
class DailyTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class DailyTaskCreate(DailyTaskBase):
    day_number: int = Field(..., ge=1, le=7)
    order: int = Field(default=0, ge=0)


class DailyTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    day_number: Optional[int] = Field(None, ge=1, le=7)
    order: Optional[int] = Field(None, ge=0)


class DailyTaskReorder(BaseModel):
    """일일 태스크 순서 변경"""
    task_id: UUID
    new_order: int = Field(..., ge=0)


class DailyTaskReorderRequest(BaseModel):
    """여러 태스크 순서 일괄 변경"""
    tasks: List[DailyTaskReorder]


class DailyTaskResponse(DailyTaskBase):
    id: UUID
    weekly_task_id: UUID
    day_number: int
    order: int
    status: TaskStatus
    is_checked: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Weekly Task schemas
class WeeklyTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class WeeklyTaskCreate(WeeklyTaskBase):
    week_number: int = Field(..., ge=1, le=4)


class WeeklyTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class WeeklyTaskResponse(WeeklyTaskBase):
    id: UUID
    monthly_goal_id: UUID
    week_number: int
    status: TaskStatus
    progress: int
    daily_generation_status: DailyGenerationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyTaskWithDaily(WeeklyTaskResponse):
    daily_goals: List[DailyGoalResponse] = []
    daily_tasks: List[DailyTaskResponse] = []


# Monthly Goal schemas
class MonthlyGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class MonthlyGoalCreate(MonthlyGoalBase):
    month_number: int = Field(..., ge=1, le=6)


class MonthlyGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class MonthlyGoalResponse(MonthlyGoalBase):
    id: UUID
    roadmap_id: UUID
    month_number: int
    status: TaskStatus
    progress: int
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlyGoalWithWeekly(MonthlyGoalResponse):
    weekly_tasks: List[WeeklyTaskResponse] = []


class MonthlyGoalFull(MonthlyGoalResponse):
    weekly_tasks: List[WeeklyTaskWithDaily] = []


# Roadmap schemas
class RoadmapBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    topic: str = Field(..., min_length=1, max_length=200)


class RoadmapCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    mode: RoadmapMode = RoadmapMode.PLANNING
    # Optional schedule fields
    daily_available_minutes: Optional[int] = Field(default=60, ge=15, le=480)
    rest_days: Optional[List[int]] = Field(default=[])
    intensity: Optional[Literal['light', 'moderate', 'intense']] = Field(default='moderate')


class RoadmapUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[RoadmapStatus] = None
    mode: Optional[RoadmapMode] = None


class RoadmapScheduleUpdate(BaseModel):
    """사용자 학습 스케줄 설정"""
    daily_available_minutes: Optional[int] = Field(None, ge=15, le=480)  # 15분~8시간
    rest_days: Optional[List[int]] = Field(None)  # [0-6] (0=일요일, 6=토요일)
    intensity: Optional[Literal['light', 'moderate', 'intense']] = None


class RoadmapResponse(RoadmapBase):
    id: UUID
    user_id: UUID
    duration_months: int
    start_date: date
    end_date: date
    mode: RoadmapMode
    status: RoadmapStatus
    progress: int
    # Finalization fields
    is_finalized: bool
    finalized_at: Optional[datetime] = None
    edit_count_after_finalize: int
    # Schedule fields
    daily_available_minutes: Optional[int] = None
    rest_days: Optional[List[int]] = None
    intensity: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadmapFinalizeResponse(BaseModel):
    """확정 응답"""
    id: UUID
    is_finalized: bool
    finalized_at: Optional[datetime] = None
    message: str


class RoadmapWithMonthly(RoadmapResponse):
    monthly_goals: List[MonthlyGoalResponse] = []


class RoadmapFull(RoadmapResponse):
    monthly_goals: List[MonthlyGoalFull] = []
