"""Roadmap generation state - Simplified."""
from typing import TypedDict, List, Optional
from datetime import date

from app.models.roadmap import RoadmapMode


class RoadmapGenerationState(TypedDict):
    """State for roadmap generation workflow."""
    # Input
    topic: str
    duration_months: int
    start_date: date
    mode: RoadmapMode
    user_id: str

    # Interview context (from SMART interview)
    interview_context: Optional[dict]

    # Generated content
    title: Optional[str]
    description: Optional[str]
    monthly_goals: List[dict]
    weekly_tasks: List[dict]
    daily_tasks: List[dict]

    # Processing state
    error_message: Optional[str]

    # Final output
    roadmap_id: Optional[str]
