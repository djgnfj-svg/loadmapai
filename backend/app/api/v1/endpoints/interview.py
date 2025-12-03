"""Interview API endpoints for SMART-based goal setting."""
from typing import Dict
from dataclasses import dataclass, field

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewSubmitRequest,
    InterviewSubmitResponse,
    InterviewQuestion,
    InterviewContext,
)
from app.ai.interview_graph import generate_questions, analyze_answers


router = APIRouter()


@dataclass
class InterviewSession:
    """In-memory interview session data."""
    topic: str
    duration_months: int
    questions: list = field(default_factory=list)  # Current round questions
    answers: list = field(default_factory=list)  # All answers
    all_questions: list = field(default_factory=list)  # All questions from all rounds
    round: int = 1


# In-memory session storage (use Redis in production)
interview_sessions: Dict[str, InterviewSession] = {}


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    data: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
):
    """Start an interview session and generate initial SMART questions."""
    try:
        result = await generate_questions(
            topic=data.topic,
            duration_months=data.duration_months,
        )

        # Store session
        session = InterviewSession(
            topic=data.topic,
            duration_months=data.duration_months,
            questions=result["questions"],
            answers=[],
            all_questions=result["questions"].copy(),  # Track all questions
            round=result["round"],
        )
        interview_sessions[result["session_id"]] = session

        return InterviewStartResponse(
            session_id=result["session_id"],
            questions=[InterviewQuestion(**q) for q in result["questions"]],
            round=result["round"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인터뷰 시작 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/submit", response_model=InterviewSubmitResponse)
async def submit_answers(
    data: InterviewSubmitRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit interview answers and get analysis results."""
    # Get session
    session = interview_sessions.get(data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인터뷰 세션을 찾을 수 없습니다.",
        )

    # Add new answers to existing answers
    new_answers = [{"question_id": a.question_id, "answer": a.answer} for a in data.answers]
    session.answers.extend(new_answers)

    try:
        result = await analyze_answers(
            topic=session.topic,
            duration_months=session.duration_months,
            session_id=data.session_id,
            questions=session.all_questions,  # Pass ALL questions from all rounds
            answers=session.answers,
            current_round=session.round,
        )

        if result["status"] == "followup_needed":
            # Update session with new questions
            session.questions = result["followup_questions"]
            session.all_questions.extend(result["followup_questions"])  # Add to history
            session.round = result["round"]

            return InterviewSubmitResponse(
                status="followup_needed",
                round=result["round"],
                followup_questions=[InterviewQuestion(**q) for q in result["followup_questions"]],
                interview_context=None,
            )
        else:
            # Interview completed - clean up session
            del interview_sessions[data.session_id]

            return InterviewSubmitResponse(
                status="completed",
                round=result["round"],
                followup_questions=None,
                interview_context=InterviewContext(**result["interview_context"]),
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"답변 분석 중 오류가 발생했습니다: {str(e)}",
        )
