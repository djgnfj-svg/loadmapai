from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Quiz, Question, UserAnswer, DailyTask
from app.models.quiz import QuizStatus
from app.schemas.quiz import (
    QuizResponse,
    QuizWithQuestions,
    QuestionResponse,
    UserAnswerResponse,
    SubmitAnswerRequest,
)


class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def get_quiz(self, quiz_id: UUID, user_id: UUID) -> Optional[Quiz]:
        """Get a quiz by ID for a specific user."""
        return self.db.query(Quiz).filter(
            Quiz.id == quiz_id,
            Quiz.user_id == user_id
        ).first()

    def get_quiz_for_daily_task(self, daily_task_id: UUID, user_id: UUID) -> Optional[Quiz]:
        """Get the latest quiz for a daily task."""
        return self.db.query(Quiz).filter(
            Quiz.daily_task_id == daily_task_id,
            Quiz.user_id == user_id
        ).order_by(Quiz.created_at.desc()).first()

    def get_quiz_with_questions(self, quiz_id: UUID, user_id: UUID) -> Optional[QuizWithQuestions]:
        """Get quiz with all questions (without answers for taking quiz)."""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            return None

        questions = self.db.query(Question).filter(
            Question.quiz_id == quiz_id
        ).order_by(Question.question_number).all()

        return QuizWithQuestions(
            id=quiz.id,
            daily_task_id=quiz.daily_task_id,
            status=quiz.status,
            total_questions=quiz.total_questions,
            score=quiz.score,
            correct_count=quiz.correct_count,
            feedback_summary=quiz.feedback_summary,
            created_at=quiz.created_at,
            updated_at=quiz.updated_at,
            questions=[
                QuestionResponse(
                    id=q.id,
                    question_type=q.question_type,
                    question_text=q.question_text,
                    options=q.options,
                    points=q.points,
                    question_number=q.question_number,
                    created_at=q.created_at,
                )
                for q in questions
            ]
        )

    def start_quiz(self, quiz_id: UUID, user_id: UUID) -> Optional[Quiz]:
        """Start a quiz (change status to in_progress)."""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            return None

        if quiz.status == QuizStatus.PENDING:
            quiz.status = QuizStatus.IN_PROGRESS
            self.db.commit()
            self.db.refresh(quiz)

        return quiz

    def submit_answer(
        self,
        question_id: UUID,
        user_id: UUID,
        answer: SubmitAnswerRequest
    ) -> Optional[UserAnswer]:
        """Submit an answer for a question."""
        # Get the question to verify it exists
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        # Check if answer already exists
        existing = self.db.query(UserAnswer).filter(
            UserAnswer.question_id == question_id,
            UserAnswer.user_id == user_id
        ).first()

        if existing:
            # Update existing answer
            existing.answer_text = answer.answer_text
            existing.selected_option = answer.selected_option
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new answer
            user_answer = UserAnswer(
                question_id=question_id,
                user_id=user_id,
                answer_text=answer.answer_text,
                selected_option=answer.selected_option,
            )
            self.db.add(user_answer)
            self.db.commit()
            self.db.refresh(user_answer)
            return user_answer

    def submit_all_answers(
        self,
        quiz_id: UUID,
        user_id: UUID,
        answers: List[SubmitAnswerRequest]
    ) -> Quiz:
        """Submit all answers and mark quiz as completed."""
        quiz = self.get_quiz(quiz_id, user_id)
        if not quiz:
            raise ValueError("Quiz not found")

        questions = self.db.query(Question).filter(
            Question.quiz_id == quiz_id
        ).order_by(Question.question_number).all()

        # Match answers to questions by order
        for i, question in enumerate(questions):
            if i < len(answers):
                self.submit_answer(question.id, user_id, answers[i])

        # Update quiz status
        quiz.status = QuizStatus.COMPLETED
        self.db.commit()
        self.db.refresh(quiz)

        return quiz

    def get_user_answers(self, quiz_id: UUID, user_id: UUID) -> List[UserAnswer]:
        """Get all user answers for a quiz."""
        questions = self.db.query(Question).filter(Question.quiz_id == quiz_id).all()
        question_ids = [q.id for q in questions]

        return self.db.query(UserAnswer).filter(
            UserAnswer.question_id.in_(question_ids),
            UserAnswer.user_id == user_id
        ).all()

    def get_quizzes_for_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Quiz]:
        """Get all quizzes for a user."""
        return self.db.query(Quiz).filter(
            Quiz.user_id == user_id
        ).order_by(Quiz.created_at.desc()).offset(skip).limit(limit).all()
