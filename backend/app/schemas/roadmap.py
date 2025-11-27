from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

from app.models.roadmap import RoadmapMode, RoadmapStatus
from app.models.monthly_goal import TaskStatus


# Daily Task schemas
class DailyTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class DailyTaskCreate(DailyTaskBase):
    day_number: int = Field(..., ge=1, le=7)


class DailyTaskResponse(DailyTaskBase):
    id: UUID
    weekly_task_id: UUID
    day_number: int
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


class WeeklyTaskResponse(WeeklyTaskBase):
    id: UUID
    monthly_goal_id: UUID
    week_number: int
    status: TaskStatus
    progress: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyTaskWithDaily(WeeklyTaskResponse):
    daily_tasks: List[DailyTaskResponse] = []


# Monthly Goal schemas
class MonthlyGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class MonthlyGoalCreate(MonthlyGoalBase):
    month_number: int = Field(..., ge=1, le=6)


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


class RoadmapUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[RoadmapStatus] = None
    mode: Optional[RoadmapMode] = None


class RoadmapResponse(RoadmapBase):
    id: UUID
    user_id: UUID
    duration_months: int
    start_date: date
    end_date: date
    mode: RoadmapMode
    status: RoadmapStatus
    progress: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadmapWithMonthly(RoadmapResponse):
    monthly_goals: List[MonthlyGoalResponse] = []


class RoadmapFull(RoadmapResponse):
    monthly_goals: List[MonthlyGoalFull] = []
