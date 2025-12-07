"""Learning mode API endpoints for questions, grading, and feedback."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.learning_service import LearningService
from app.schemas.learning import (
    QuestionResponse,
    QuestionWithAnswer,
    SubmitAnswerRequest,
    UserAnswerResponse,
    QuestionResultResponse,
    DailyFeedbackResponse,
    CompleteDayResponse,
    WrongQuestionResponse,
    ReviewSessionResponse,
    LearningDayInfoResponse,
    LearningWeekInfoResponse,
)

router = APIRouter()


# ============ Question Endpoints ============

@router.get(
    "/daily-tasks/{task_id}/questions",
    response_model=List[QuestionResponse],
)
async def get_questions_for_day(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all questions for a daily task.

    Returns questions without correct answers (for solving).
    User's existing answers are included if any.
    """
    service = LearningService(db)
    questions = service.get_questions(task_id, current_user.id)

    return [
        QuestionResponse(
            id=q.id,
            daily_task_id=q.daily_task_id,
            question_type=q.question_type,
            question_text=q.question_text,
            choices=q.choices,
            hint=q.hint,
            order=q.order,
            user_answer=UserAnswerResponse(
                id=q.user_answer.id,
                question_id=q.user_answer.question_id,
                answer_text=q.user_answer.answer_text,
                is_correct=q.user_answer.is_correct,
                score=q.user_answer.score,
                feedback=q.user_answer.feedback,
                submitted_at=q.user_answer.submitted_at,
                graded_at=q.user_answer.graded_at,
            ) if q.user_answer else None,
        )
        for q in questions
    ]


@router.post(
    "/questions/{question_id}/submit",
    response_model=UserAnswerResponse,
)
async def submit_answer(
    question_id: UUID,
    data: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer for a question.

    Saves the answer without grading. Grading happens when the day is completed.
    Can be called multiple times to update the answer.
    """
    service = LearningService(db)
    answer = service.submit_answer(question_id, current_user.id, data.answer_text)

    return UserAnswerResponse(
        id=answer.id,
        question_id=answer.question_id,
        answer_text=answer.answer_text,
        is_correct=answer.is_correct,
        score=answer.score,
        feedback=answer.feedback,
        submitted_at=answer.submitted_at,
        graded_at=answer.graded_at,
    )


# ============ Day Completion & Feedback ============

@router.post(
    "/daily-tasks/{task_id}/complete-day",
    response_model=CompleteDayResponse,
)
async def complete_day(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a day: grade all answers and generate feedback.

    All questions must be answered before completing.
    Returns feedback with individual question results.
    """
    service = LearningService(db)
    feedback = await service.complete_day(task_id, current_user.id)

    # Get question results
    questions = service.get_questions(task_id, current_user.id)
    question_results = [
        QuestionResultResponse(
            question_id=q.id,
            question_type=q.question_type,
            question_text=q.question_text,
            your_answer=q.user_answer.answer_text if q.user_answer else "",
            correct_answer=q.correct_answer,
            is_correct=q.user_answer.is_correct if q.user_answer else False,
            score=q.user_answer.score,
            feedback=q.user_answer.feedback or "",
            explanation=q.explanation,
        )
        for q in questions
        if q.user_answer
    ]

    # Check if all days in the week are completed
    week_info = service.get_week_info(feedback.weekly_task_id, current_user.id)
    week_completed = week_info["is_completed"]

    return CompleteDayResponse(
        feedback=DailyFeedbackResponse(
            id=feedback.id,
            weekly_task_id=feedback.weekly_task_id,
            day_number=feedback.day_number,
            total_questions=feedback.total_questions,
            correct_count=feedback.correct_count,
            accuracy_rate=feedback.accuracy_rate,
            is_passed=feedback.is_passed,
            summary=feedback.summary,
            strengths=feedback.strengths,
            improvements=feedback.improvements,
            question_results=question_results,
            created_at=feedback.created_at,
        ),
        next_day_available=feedback.is_passed,
        week_completed=week_completed,
    )


@router.get(
    "/weekly-tasks/{task_id}/day/{day_number}/feedback",
    response_model=Optional[DailyFeedbackResponse],
)
async def get_daily_feedback(
    task_id: UUID,
    day_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback for a specific day.

    Returns None if the day hasn't been completed yet.
    """
    service = LearningService(db)
    feedback = service.get_daily_feedback(task_id, day_number, current_user.id)

    if not feedback:
        return None

    return DailyFeedbackResponse(
        id=feedback.id,
        weekly_task_id=feedback.weekly_task_id,
        day_number=feedback.day_number,
        total_questions=feedback.total_questions,
        correct_count=feedback.correct_count,
        accuracy_rate=feedback.accuracy_rate,
        is_passed=feedback.is_passed,
        summary=feedback.summary,
        strengths=feedback.strengths,
        improvements=feedback.improvements,
        question_results=None,  # Not loading question results here
        created_at=feedback.created_at,
    )


# ============ Wrong Questions & Review ============

@router.get(
    "/weekly-tasks/{task_id}/wrong-questions",
    response_model=List[WrongQuestionResponse],
)
async def get_wrong_questions(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all wrong questions for a weekly task.

    Returns questions with correct answers and user's wrong answers.
    """
    service = LearningService(db)
    wrong_questions = service.get_wrong_questions(task_id, current_user.id)

    return [
        WrongQuestionResponse(
            question=QuestionWithAnswer(
                id=wq["question"].id,
                daily_task_id=wq["question"].daily_task_id,
                question_type=wq["question"].question_type,
                question_text=wq["question"].question_text,
                choices=wq["question"].choices,
                hint=wq["question"].hint,
                order=wq["question"].order,
                correct_answer=wq["question"].correct_answer,
                explanation=wq["question"].explanation,
                user_answer=UserAnswerResponse(
                    id=wq["question"].user_answer.id,
                    question_id=wq["question"].user_answer.question_id,
                    answer_text=wq["question"].user_answer.answer_text,
                    is_correct=wq["question"].user_answer.is_correct,
                    score=wq["question"].user_answer.score,
                    feedback=wq["question"].user_answer.feedback,
                    submitted_at=wq["question"].user_answer.submitted_at,
                    graded_at=wq["question"].user_answer.graded_at,
                ) if wq["question"].user_answer else None,
            ),
            your_answer=wq["your_answer"],
            day_number=wq["day_number"],
        )
        for wq in wrong_questions
    ]


@router.post(
    "/weekly-tasks/{task_id}/generate-review",
    response_model=ReviewSessionResponse,
)
async def generate_review_session(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a review session based on wrong questions.

    Creates variation questions from wrong answers for review.
    Can only be called once per week.
    """
    service = LearningService(db)
    review_task = await service.generate_review_session(task_id, current_user.id)

    # Get review questions
    questions = service.get_questions(review_task.id, current_user.id)

    return ReviewSessionResponse(
        daily_task_id=review_task.id,
        total_questions=len(questions),
        questions=[
            QuestionResponse(
                id=q.id,
                daily_task_id=q.daily_task_id,
                question_type=q.question_type,
                question_text=q.question_text,
                choices=q.choices,
                hint=q.hint,
                order=q.order,
                user_answer=None,
            )
            for q in questions
        ],
    )


# ============ Learning Info ============

@router.get(
    "/daily-tasks/{task_id}/info",
    response_model=LearningDayInfoResponse,
)
async def get_day_info(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get learning day information.

    Returns progress and completion status for a specific day.
    """
    service = LearningService(db)
    info = service.get_day_info(task_id, current_user.id)

    feedback_response = None
    if info["feedback"]:
        feedback_response = DailyFeedbackResponse(
            id=info["feedback"].id,
            weekly_task_id=info["feedback"].weekly_task_id,
            day_number=info["feedback"].day_number,
            total_questions=info["feedback"].total_questions,
            correct_count=info["feedback"].correct_count,
            accuracy_rate=info["feedback"].accuracy_rate,
            is_passed=info["feedback"].is_passed,
            summary=info["feedback"].summary,
            strengths=info["feedback"].strengths,
            improvements=info["feedback"].improvements,
            question_results=None,
            created_at=info["feedback"].created_at,
        )

    return LearningDayInfoResponse(
        daily_task_id=info["daily_task_id"],
        weekly_task_id=info["weekly_task_id"],
        day_number=info["day_number"],
        title=info["title"],
        description=info["description"],
        total_questions=info["total_questions"],
        answered_count=info["answered_count"],
        is_completed=info["is_completed"],
        feedback=feedback_response,
    )


@router.get(
    "/weekly-tasks/{task_id}/info",
    response_model=LearningWeekInfoResponse,
)
async def get_week_info(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get learning week information.

    Returns progress and completion status for all days in the week.
    """
    service = LearningService(db)
    info = service.get_week_info(task_id, current_user.id)

    days_response = []
    for day_info in info["days"]:
        feedback_response = None
        if day_info["feedback"]:
            feedback_response = DailyFeedbackResponse(
                id=day_info["feedback"].id,
                weekly_task_id=day_info["feedback"].weekly_task_id,
                day_number=day_info["feedback"].day_number,
                total_questions=day_info["feedback"].total_questions,
                correct_count=day_info["feedback"].correct_count,
                accuracy_rate=day_info["feedback"].accuracy_rate,
                is_passed=day_info["feedback"].is_passed,
                summary=day_info["feedback"].summary,
                strengths=day_info["feedback"].strengths,
                improvements=day_info["feedback"].improvements,
                question_results=None,
                created_at=day_info["feedback"].created_at,
            )

        days_response.append(LearningDayInfoResponse(
            daily_task_id=day_info["daily_task_id"],
            weekly_task_id=day_info["weekly_task_id"],
            day_number=day_info["day_number"],
            title=day_info["title"],
            description=day_info["description"],
            total_questions=day_info["total_questions"],
            answered_count=day_info["answered_count"],
            is_completed=day_info["is_completed"],
            feedback=feedback_response,
        ))

    return LearningWeekInfoResponse(
        weekly_task_id=info["weekly_task_id"],
        week_number=info["week_number"],
        title=info["title"],
        description=info["description"],
        days=days_response,
        total_questions=info["total_questions"],
        correct_count=info["correct_count"],
        accuracy_rate=info["accuracy_rate"],
        is_completed=info["is_completed"],
        review_available=info["review_available"],
    )
