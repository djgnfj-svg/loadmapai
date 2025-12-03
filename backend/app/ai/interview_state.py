"""Interview state for SMART-based goal setting."""
from typing import TypedDict, List, Optional


class InterviewState(TypedDict):
    """State for SMART interview workflow."""
    # Input
    topic: str
    duration_months: int
    session_id: str

    # Questions & Answers
    questions: List[dict]  # Current questions
    answers: List[dict]  # All answers so far

    # Progress
    round: int  # Current round (1-3)
    needs_followup: bool

    # Output
    interview_context: Optional[dict]
    error_message: Optional[str]
