from typing import TypedDict, List, Optional, Annotated
from operator import add
from datetime import date

from app.models.roadmap import RoadmapMode


class MonthlyGoalData(TypedDict):
    month_number: int
    title: str
    description: str


class WeeklyTaskData(TypedDict):
    week_number: int
    title: str
    description: str


class DailyTaskData(TypedDict):
    day_number: int
    title: str
    description: str


class RoadmapGenerationState(TypedDict):
    # Input
    topic: str
    duration_months: int
    start_date: date
    mode: RoadmapMode
    user_id: str

    # Optional context (for future personalization)
    interview_context: Optional[str]
    daily_time: Optional[str]

    # Schedule info
    daily_available_minutes: Optional[int]
    rest_days: Optional[List[int]]
    intensity: Optional[str]

    # Web search results
    search_results: Optional[List[dict]]
    search_context: Optional[str]

    # Generated content
    title: Optional[str]
    description: Optional[str]
    monthly_goals: Annotated[List[MonthlyGoalData], add]
    weekly_tasks: Annotated[List[dict], add]
    daily_tasks: Annotated[List[dict], add]

    # Processing state
    current_month: int
    current_week: int
    validation_passed: bool
    error_message: Optional[str]
    retry_count: int

    # Final output
    roadmap_id: Optional[str]
