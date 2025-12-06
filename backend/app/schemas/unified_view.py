"""Schemas for unified view API responses."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from uuid import UUID


class TodayDailyTask(BaseModel):
    """Daily task with roadmap context for unified view."""

    id: UUID
    title: str
    description: Optional[str] = None
    day_number: int
    order: int
    is_checked: bool
    actual_date: date

    # Roadmap context
    roadmap_id: UUID
    roadmap_title: str
    roadmap_topic: str

    # Weekly task context
    weekly_task_id: UUID
    weekly_task_title: str

    # Monthly goal context
    monthly_goal_id: UUID
    monthly_goal_title: str

    class Config:
        from_attributes = True


class WeeklyTaskSummary(BaseModel):
    """Weekly task summary with daily tasks for unified view."""

    id: UUID
    title: str
    description: Optional[str] = None
    week_number: int
    progress: int

    # Roadmap context
    roadmap_id: UUID
    roadmap_title: str
    roadmap_topic: str

    # Monthly goal context
    monthly_goal_id: UUID
    monthly_goal_title: str

    # Daily tasks
    daily_tasks: List[TodayDailyTask]

    # Date range
    week_start: date
    week_end: date

    class Config:
        from_attributes = True


class UnifiedViewResponse(BaseModel):
    """Response for unified today view endpoint."""

    target_date: date
    today_tasks: List[TodayDailyTask]
    current_week: List[WeeklyTaskSummary]

    # Statistics
    today_total: int
    today_completed: int
    week_total: int
    week_completed: int

    class Config:
        from_attributes = True
