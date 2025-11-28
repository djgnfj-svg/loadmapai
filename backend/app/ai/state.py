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

    # Generated content
    title: Optional[str]
    description: Optional[str]
    monthly_goals: Annotated[List[MonthlyGoalData], add]
    weekly_tasks: Annotated[List[dict], add]  # {month_number: [WeeklyTaskData]}
    daily_tasks: Annotated[List[dict], add]  # {month_number: {week_number: [DailyTaskData]}}

    # Processing state
    current_month: int
    current_week: int
    validation_passed: bool
    error_message: Optional[str]
    retry_count: int

    # Final output
    roadmap_id: Optional[str]


# ============ Question Generation State ============

class QuestionData(TypedDict):
    question_type: str  # "multiple_choice", "short_answer", "essay"
    question_text: str
    options: Optional[List[str]]  # For multiple choice
    correct_answer: Optional[str]
    explanation: Optional[str]
    points: int


class QuestionGenerationState(TypedDict):
    # Input
    daily_task_id: str
    daily_task_title: str
    daily_task_description: str
    weekly_task_title: str
    monthly_goal_title: str
    roadmap_topic: str
    num_questions: int
    user_id: str

    # Analysis results
    key_concepts: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    question_focus_areas: List[str]

    # Generated content
    questions: List[QuestionData]

    # Validation
    validation_passed: bool
    error_message: Optional[str]
    retry_count: int

    # Output
    quiz_id: Optional[str]


# ============ Grading State ============

class AnswerData(TypedDict):
    question_id: str
    question_type: str
    question_text: str
    correct_answer: Optional[str]
    user_answer: str
    selected_option: Optional[str]
    options: Optional[List[str]]


class GradingResultData(TypedDict):
    question_id: str
    is_correct: bool
    score: float  # 0-100, allows partial credit for essay
    feedback: str


class GradingState(TypedDict):
    # Input
    quiz_id: str
    user_id: str
    answers: List[AnswerData]
    topic: str  # Daily task title for context

    # Grading results
    grading_results: List[GradingResultData]
    total_score: float
    correct_count: int
    total_questions: int

    # Overall feedback
    feedback_summary: str
    strengths: List[str]
    areas_to_improve: List[str]

    # Processing state
    current_answer_index: int
    error_message: Optional[str]
