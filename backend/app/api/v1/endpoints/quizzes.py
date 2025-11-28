from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.quiz import QuizStatus
from app.schemas.quiz import (
    QuizResponse,
    QuizWithQuestions,
    QuizResult,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    SubmitAnswerRequest,
    UserAnswerResponse,
)
from app.services.quiz_service import QuizService
from app.api.deps import get_current_user
from app.ai.question_graph import generate_quiz
from app.ai.grading_graph import grade_quiz


router = APIRouter()


@router.get("", response_model=List[QuizResponse])
async def list_quizzes(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of user's quizzes."""
    service = QuizService(db)
    return service.get_quizzes_for_user(current_user.id, skip, limit)


@router.get("/daily-task/{daily_task_id}", response_model=QuizResponse)
async def get_quiz_for_daily_task(
    daily_task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the latest quiz for a daily task."""
    service = QuizService(db)
    quiz = service.get_quiz_for_daily_task(daily_task_id, current_user.id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 태스크의 퀴즈가 없습니다.",
        )
    return quiz


@router.post("/daily-task/{daily_task_id}/generate", response_model=QuizGenerateResponse)
async def generate_quiz_for_daily_task(
    daily_task_id: UUID,
    num_questions: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new quiz for a daily task using AI."""
    try:
        result = await generate_quiz(
            daily_task_id=str(daily_task_id),
            user_id=str(current_user.id),
            num_questions=min(max(num_questions, 5), 10),  # Clamp to 5-10
            db=db,
        )

        return QuizGenerateResponse(
            quiz_id=UUID(result["quiz_id"]),
            message=f"퀴즈가 생성되었습니다. {result['total_questions']}개의 문제가 포함되어 있습니다.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"퀴즈 생성 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/{quiz_id}", response_model=QuizWithQuestions)
async def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a quiz with its questions."""
    service = QuizService(db)
    quiz = service.get_quiz_with_questions(quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다.",
        )
    return quiz


@router.post("/{quiz_id}/start", response_model=QuizResponse)
async def start_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a quiz (change status to in_progress)."""
    service = QuizService(db)
    quiz = service.start_quiz(quiz_id, current_user.id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다.",
        )
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    quiz_id: UUID,
    request: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit all answers and complete the quiz."""
    service = QuizService(db)
    try:
        quiz = service.submit_all_answers(quiz_id, current_user.id, request.answers)
        return QuizSubmitResponse(
            quiz_id=quiz.id,
            message="답변이 제출되었습니다. 채점 중입니다.",
            status=quiz.status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{quiz_id}/grade", response_model=QuizResult)
async def grade_quiz_endpoint(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grade a completed quiz using AI."""
    service = QuizService(db)
    quiz = service.get_quiz(quiz_id, current_user.id)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다.",
        )

    if quiz.status not in [QuizStatus.COMPLETED, QuizStatus.GRADED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="퀴즈가 아직 완료되지 않았습니다.",
        )

    try:
        result = await grade_quiz(
            quiz_id=str(quiz_id),
            user_id=str(current_user.id),
            db=db,
        )

        # Get updated quiz with questions and answers
        quiz_data = service.get_quiz_with_questions(quiz_id, current_user.id)
        user_answers = service.get_user_answers(quiz_id, current_user.id)

        return QuizResult(
            quiz_id=quiz_id,
            status=QuizStatus.GRADED,
            total_questions=result["total_questions"],
            correct_count=result["correct_count"],
            score=result["total_score"],
            feedback_summary=result["feedback_summary"],
            questions=quiz_data.questions if quiz_data else [],
            user_answers=[
                UserAnswerResponse(
                    id=ua.id,
                    question_id=ua.question_id,
                    answer_text=ua.answer_text,
                    selected_option=ua.selected_option,
                    is_correct=ua.is_correct,
                    score=ua.score,
                    feedback=ua.feedback,
                    created_at=ua.created_at,
                )
                for ua in user_answers
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채점 중 오류가 발생했습니다: {str(e)}",
        )


@router.post("/{quiz_id}/reset", response_model=QuizResponse)
async def reset_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reset a quiz: 기존 답변 삭제, 상태를 PENDING으로 변경."""
    service = QuizService(db)
    try:
        quiz = service.reset_quiz(quiz_id, current_user.id)
        return quiz
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/questions/{question_id}/answer", response_model=UserAnswerResponse)
async def submit_single_answer(
    question_id: UUID,
    answer: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer for a single question."""
    service = QuizService(db)
    user_answer = service.submit_answer(question_id, current_user.id, answer)
    if not user_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문제를 찾을 수 없습니다.",
        )
    return user_answer
