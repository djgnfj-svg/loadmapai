"""Service for Learning mode - question management, grading, and feedback."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models import (
    Roadmap, MonthlyGoal, WeeklyTask, DailyTask, RoadmapMode
)
from app.models.question import Question, QuestionType
from app.models.user_answer import UserAnswer
from app.models.daily_feedback import DailyFeedback
from app.ai.llm import invoke_llm_json, DEFAULT_ANALYTICAL_TEMP, DEFAULT_CREATIVE_TEMP
from app.ai.prompts.learning_templates import (
    LEARNING_DAILY_QUESTIONS_PROMPT,
    GRADING_PROMPT,
    DAILY_FEEDBACK_PROMPT,
    REVIEW_QUESTIONS_PROMPT,
    build_questions_summary,
    build_wrong_questions_list,
)


_executor = ThreadPoolExecutor(max_workers=2)


class LearningService:
    """Service for managing learning mode questions and grading."""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Query Methods ====================

    def get_daily_task_with_context(
        self, daily_task_id: UUID, user_id: UUID
    ) -> tuple[DailyTask, Roadmap]:
        """Get daily task with roadmap context and verify ownership."""
        daily_task = (
            self.db.query(DailyTask)
            .options(
                joinedload(DailyTask.weekly_task)
                .joinedload(WeeklyTask.monthly_goal)
                .joinedload(MonthlyGoal.roadmap)
            )
            .join(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(DailyTask.id == daily_task_id, Roadmap.user_id == user_id)
            .first()
        )
        if not daily_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily task not found",
            )
        return daily_task, daily_task.weekly_task.monthly_goal.roadmap

    def get_weekly_task_with_context(
        self, weekly_task_id: UUID, user_id: UUID
    ) -> tuple[WeeklyTask, Roadmap]:
        """Get weekly task with roadmap context and verify ownership."""
        weekly_task = (
            self.db.query(WeeklyTask)
            .options(
                joinedload(WeeklyTask.monthly_goal).joinedload(MonthlyGoal.roadmap)
            )
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(WeeklyTask.id == weekly_task_id, Roadmap.user_id == user_id)
            .first()
        )
        if not weekly_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly task not found",
            )
        return weekly_task, weekly_task.monthly_goal.roadmap

    def get_questions(self, daily_task_id: UUID, user_id: UUID) -> List[Question]:
        """Get all questions for a daily task with user's answers."""
        daily_task, roadmap = self.get_daily_task_with_context(daily_task_id, user_id)

        # Verify LEARNING mode
        if roadmap.mode != RoadmapMode.LEARNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This roadmap is not in LEARNING mode",
            )

        questions = (
            self.db.query(Question)
            .options(joinedload(Question.user_answer))
            .filter(Question.daily_task_id == daily_task_id)
            .order_by(Question.order)
            .all()
        )

        return questions

    def get_question(self, question_id: UUID, user_id: UUID) -> Question:
        """Get a single question with ownership verification."""
        question = (
            self.db.query(Question)
            .options(joinedload(Question.user_answer))
            .join(DailyTask)
            .join(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(Question.id == question_id, Roadmap.user_id == user_id)
            .first()
        )
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        return question

    # ==================== Answer Submission ====================

    def submit_answer(
        self, question_id: UUID, user_id: UUID, answer_text: str
    ) -> UserAnswer:
        """Submit an answer for a question (no grading yet)."""
        question = self.get_question(question_id, user_id)

        # Check if already answered
        existing = (
            self.db.query(UserAnswer)
            .filter(
                UserAnswer.question_id == question_id,
                UserAnswer.user_id == user_id,
            )
            .first()
        )

        if existing:
            # Update existing answer
            existing.answer_text = answer_text
            existing.submitted_at = datetime.now(timezone.utc)
            existing.is_correct = None  # Reset grading
            existing.score = None
            existing.feedback = None
            existing.graded_at = None
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new answer
        user_answer = UserAnswer(
            question_id=question_id,
            user_id=user_id,
            answer_text=answer_text,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(user_answer)
        self.db.commit()
        self.db.refresh(user_answer)

        return user_answer

    # ==================== Day Completion & Grading ====================

    async def complete_day(
        self, daily_task_id: UUID, user_id: UUID
    ) -> DailyFeedback:
        """Complete a day: grade all answers and generate feedback."""
        daily_task, roadmap = self.get_daily_task_with_context(daily_task_id, user_id)

        # Verify LEARNING mode
        if roadmap.mode != RoadmapMode.LEARNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This roadmap is not in LEARNING mode",
            )

        # Get all questions with answers
        questions = (
            self.db.query(Question)
            .options(joinedload(Question.user_answer))
            .filter(Question.daily_task_id == daily_task_id)
            .order_by(Question.order)
            .all()
        )

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No questions found for this day",
            )

        # Check if all questions are answered
        unanswered = [q for q in questions if not q.user_answer]
        if unanswered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please answer all questions before completing. {len(unanswered)} questions remaining.",
            )

        # Check for existing feedback
        existing_feedback = (
            self.db.query(DailyFeedback)
            .filter(
                DailyFeedback.weekly_task_id == daily_task.weekly_task_id,
                DailyFeedback.day_number == daily_task.day_number,
                DailyFeedback.user_id == user_id,
            )
            .first()
        )

        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This day has already been completed",
            )

        # Grade all answers
        loop = asyncio.get_event_loop()
        grading_results = []

        for question in questions:
            result = await loop.run_in_executor(
                _executor,
                self._grade_answer_sync,
                question,
                question.user_answer.answer_text,
            )
            result["question_id"] = str(question.id)
            result["question_type"] = question.question_type.value
            result["question_text"] = question.question_text
            result["your_answer"] = question.user_answer.answer_text
            result["correct_answer"] = question.correct_answer
            result["explanation"] = question.explanation
            grading_results.append(result)

            # Update user answer with grading
            question.user_answer.is_correct = result["is_correct"]
            question.user_answer.score = result.get("score")
            question.user_answer.feedback = result["feedback"]
            question.user_answer.graded_at = datetime.now(timezone.utc)

        self.db.commit()

        # Calculate stats
        total = len(questions)
        correct = sum(1 for r in grading_results if r["is_correct"])
        accuracy = correct / total if total > 0 else 0.0
        is_passed = accuracy >= 0.7

        # Generate daily feedback
        feedback_data = await loop.run_in_executor(
            _executor,
            self._generate_daily_feedback_sync,
            roadmap.topic,
            daily_task.weekly_task.monthly_goal.month_number,
            daily_task.weekly_task.week_number,
            daily_task.day_number,
            total,
            correct,
            accuracy,
            grading_results,
        )

        # Save feedback
        daily_feedback = DailyFeedback(
            weekly_task_id=daily_task.weekly_task_id,
            day_number=daily_task.day_number,
            user_id=user_id,
            total_questions=total,
            correct_count=correct,
            accuracy_rate=accuracy,
            is_passed=is_passed,
            summary=feedback_data.get("summary", "학습을 완료했습니다."),
            strengths=feedback_data.get("strengths", []),
            improvements=feedback_data.get("improvements", []),
        )
        self.db.add(daily_feedback)

        # Mark daily task as completed
        daily_task.is_checked = True
        daily_task.status = "COMPLETED"

        self.db.commit()
        self.db.refresh(daily_feedback)

        # Update weekly progress
        self._update_weekly_progress(daily_task.weekly_task_id)

        return daily_feedback

    def _grade_answer_sync(self, question: Question, user_answer: str) -> dict:
        """Synchronously grade a single answer using AI."""
        prompt = GRADING_PROMPT.format(
            question_type=question.question_type.value,
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            explanation=question.explanation or "",
            user_answer=user_answer,
        )

        try:
            result = invoke_llm_json(prompt, temperature=DEFAULT_ANALYTICAL_TEMP)
            return {
                "is_correct": result.get("is_correct", False),
                "score": result.get("score"),
                "feedback": result.get("feedback", ""),
                "key_points_matched": result.get("key_points_matched", []),
                "key_points_missed": result.get("key_points_missed", []),
            }
        except Exception as e:
            # Fallback: simple string matching for non-essay
            is_correct = False
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                is_correct = user_answer.strip() == question.correct_answer.strip()
            elif question.question_type == QuestionType.SHORT_ANSWER:
                is_correct = (
                    user_answer.strip().lower()
                    == question.correct_answer.strip().lower()
                )

            return {
                "is_correct": is_correct,
                "score": 100 if is_correct else 0,
                "feedback": "정답입니다!" if is_correct else f"정답은 '{question.correct_answer}'입니다.",
                "key_points_matched": [],
                "key_points_missed": [],
            }

    def _generate_daily_feedback_sync(
        self,
        topic: str,
        month_number: int,
        week_number: int,
        day_number: int,
        total_questions: int,
        correct_count: int,
        accuracy_rate: float,
        grading_results: list,
    ) -> dict:
        """Synchronously generate daily feedback using AI."""
        questions_summary = build_questions_summary(
            [
                {
                    "is_correct": r["is_correct"],
                    "question_type": r["question_type"],
                    "question_text": r["question_text"],
                }
                for r in grading_results
            ]
        )

        prompt = DAILY_FEEDBACK_PROMPT.format(
            topic=topic,
            month_number=month_number,
            week_number=week_number,
            day_number=day_number,
            total_questions=total_questions,
            correct_count=correct_count,
            accuracy_rate=round(accuracy_rate * 100, 1),
            questions_summary=questions_summary,
        )

        try:
            result = invoke_llm_json(prompt, temperature=DEFAULT_CREATIVE_TEMP)
            return {
                "summary": result.get("summary", ""),
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", []),
                "tomorrow_focus": result.get("tomorrow_focus", ""),
            }
        except Exception as e:
            # Fallback feedback
            if accuracy_rate >= 0.8:
                return {
                    "summary": f"훌륭합니다! {round(accuracy_rate * 100)}%의 정답률로 오늘 학습을 잘 마무리했습니다.",
                    "strengths": ["학습 내용을 잘 이해하고 있습니다"],
                    "improvements": ["더 심화된 내용에 도전해보세요"],
                }
            elif accuracy_rate >= 0.7:
                return {
                    "summary": f"좋은 결과입니다! {round(accuracy_rate * 100)}%의 정답률로 합격했습니다.",
                    "strengths": ["기본 개념을 잘 파악하고 있습니다"],
                    "improvements": ["틀린 문제를 다시 복습해보세요"],
                }
            else:
                return {
                    "summary": f"{round(accuracy_rate * 100)}%의 정답률입니다. 조금 더 복습이 필요합니다.",
                    "strengths": ["꾸준히 학습하는 자세가 좋습니다"],
                    "improvements": ["오늘 학습 내용을 다시 한번 복습해보세요"],
                }

    def _update_weekly_progress(self, weekly_task_id: UUID):
        """Update weekly task progress based on completed days."""
        weekly = (
            self.db.query(WeeklyTask)
            .options(joinedload(WeeklyTask.daily_tasks))
            .filter(WeeklyTask.id == weekly_task_id)
            .first()
        )
        if not weekly:
            return

        total = len(weekly.daily_tasks)
        completed = sum(1 for d in weekly.daily_tasks if d.is_checked)

        weekly.progress = int((completed / total) * 100) if total > 0 else 0
        weekly.status = "COMPLETED" if weekly.progress == 100 else (
            "IN_PROGRESS" if weekly.progress > 0 else "PENDING"
        )

        self.db.commit()

    # ==================== Wrong Questions & Review ====================

    def get_wrong_questions(
        self, weekly_task_id: UUID, user_id: UUID
    ) -> List[dict]:
        """Get all wrong questions for a weekly task."""
        weekly_task, _ = self.get_weekly_task_with_context(weekly_task_id, user_id)

        # Get all daily tasks for this week
        daily_tasks = (
            self.db.query(DailyTask)
            .filter(DailyTask.weekly_task_id == weekly_task_id)
            .all()
        )

        wrong_questions = []
        for daily_task in daily_tasks:
            questions = (
                self.db.query(Question)
                .options(joinedload(Question.user_answer))
                .filter(Question.daily_task_id == daily_task.id)
                .all()
            )

            for q in questions:
                if q.user_answer and q.user_answer.is_correct is False:
                    wrong_questions.append({
                        "question": q,
                        "your_answer": q.user_answer.answer_text,
                        "day_number": daily_task.day_number,
                    })

        return wrong_questions

    def get_daily_feedback(
        self, weekly_task_id: UUID, day_number: int, user_id: UUID
    ) -> Optional[DailyFeedback]:
        """Get feedback for a specific day."""
        weekly_task, _ = self.get_weekly_task_with_context(weekly_task_id, user_id)

        feedback = (
            self.db.query(DailyFeedback)
            .filter(
                DailyFeedback.weekly_task_id == weekly_task_id,
                DailyFeedback.day_number == day_number,
                DailyFeedback.user_id == user_id,
            )
            .first()
        )

        return feedback

    async def generate_review_session(
        self, weekly_task_id: UUID, user_id: UUID
    ) -> DailyTask:
        """Generate a review session with wrong questions."""
        weekly_task, roadmap = self.get_weekly_task_with_context(weekly_task_id, user_id)

        if weekly_task.review_generated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review session has already been generated for this week",
            )

        wrong_questions = self.get_wrong_questions(weekly_task_id, user_id)

        if not wrong_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No wrong questions to review",
            )

        # Build wrong questions list for prompt
        wrong_list = [
            {
                "question_id": str(wq["question"].id),
                "question_type": wq["question"].question_type.value,
                "question_text": wq["question"].question_text,
                "correct_answer": wq["question"].correct_answer,
                "user_answer": wq["your_answer"],
                "explanation": wq["question"].explanation or "",
            }
            for wq in wrong_questions
        ]

        # Generate review questions using AI
        loop = asyncio.get_event_loop()
        review_data = await loop.run_in_executor(
            _executor,
            self._generate_review_questions_sync,
            wrong_list,
        )

        # Create review daily task
        review_task = DailyTask(
            weekly_task_id=weekly_task_id,
            day_number=8,  # Special day number for review
            order=0,
            title="틀린 문제 복습",
            description=f"이번 주 틀린 {len(wrong_questions)}개 문제를 복습합니다.",
            is_review_task=True,
            review_source_ids=[wq["question"].id for wq in wrong_questions],
        )
        self.db.add(review_task)
        self.db.flush()  # Get the ID

        # Create review questions
        review_questions = review_data.get("review_questions", [])
        for order, rq in enumerate(review_questions):
            question = Question(
                daily_task_id=review_task.id,
                question_type=QuestionType(rq.get("question_type", "SHORT_ANSWER")),
                question_text=rq["question_text"],
                choices=rq.get("choices"),
                correct_answer=rq["correct_answer"],
                hint=rq.get("hint"),
                explanation=rq.get("explanation"),
                order=order,
            )
            self.db.add(question)

        # Mark review as generated
        weekly_task.review_generated = True

        self.db.commit()
        self.db.refresh(review_task)

        return review_task

    def _generate_review_questions_sync(self, wrong_questions: list) -> dict:
        """Synchronously generate review questions using AI."""
        wrong_list_str = build_wrong_questions_list(wrong_questions)

        prompt = REVIEW_QUESTIONS_PROMPT.format(
            wrong_questions_list=wrong_list_str
        )

        try:
            result = invoke_llm_json(prompt, temperature=DEFAULT_CREATIVE_TEMP)
            return result
        except Exception as e:
            # Fallback: create simple review questions from wrong ones
            return {
                "review_questions": [
                    {
                        "original_question_id": wq["question_id"],
                        "question_type": wq["question_type"],
                        "question_text": f"[복습] {wq['question_text']}",
                        "correct_answer": wq["correct_answer"],
                        "hint": "이전에 틀린 문제입니다. 다시 한번 생각해보세요.",
                        "explanation": wq["explanation"],
                        "review_focus": "이전 오답 복습",
                    }
                    for wq in wrong_questions[:5]  # Limit to 5 questions
                ]
            }

    # ==================== Learning Info ====================

    def get_day_info(self, daily_task_id: UUID, user_id: UUID) -> dict:
        """Get learning day information."""
        daily_task, roadmap = self.get_daily_task_with_context(daily_task_id, user_id)

        questions = (
            self.db.query(Question)
            .options(joinedload(Question.user_answer))
            .filter(Question.daily_task_id == daily_task_id)
            .all()
        )

        answered_count = sum(1 for q in questions if q.user_answer)

        feedback = (
            self.db.query(DailyFeedback)
            .filter(
                DailyFeedback.weekly_task_id == daily_task.weekly_task_id,
                DailyFeedback.day_number == daily_task.day_number,
                DailyFeedback.user_id == user_id,
            )
            .first()
        )

        return {
            "daily_task_id": daily_task.id,
            "weekly_task_id": daily_task.weekly_task_id,
            "day_number": daily_task.day_number,
            "title": daily_task.title,
            "description": daily_task.description,
            "total_questions": len(questions),
            "answered_count": answered_count,
            "is_completed": daily_task.is_checked,
            "feedback": feedback,
        }

    def get_week_info(self, weekly_task_id: UUID, user_id: UUID) -> dict:
        """Get learning week information."""
        weekly_task, roadmap = self.get_weekly_task_with_context(weekly_task_id, user_id)

        daily_tasks = (
            self.db.query(DailyTask)
            .filter(DailyTask.weekly_task_id == weekly_task_id)
            .order_by(DailyTask.day_number)
            .all()
        )

        days_info = []
        total_questions = 0
        correct_count = 0

        for dt in daily_tasks:
            day_info = self.get_day_info(dt.id, user_id)
            days_info.append(day_info)

            if day_info["feedback"]:
                total_questions += day_info["feedback"].total_questions
                correct_count += day_info["feedback"].correct_count

        accuracy_rate = correct_count / total_questions if total_questions > 0 else 0.0

        # Check if there are any wrong questions
        wrong_questions = self.get_wrong_questions(weekly_task_id, user_id)
        review_available = len(wrong_questions) > 0 and not weekly_task.review_generated

        return {
            "weekly_task_id": weekly_task.id,
            "week_number": weekly_task.week_number,
            "title": weekly_task.title,
            "description": weekly_task.description,
            "days": days_info,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy_rate": accuracy_rate,
            "is_completed": weekly_task.progress == 100,
            "review_available": review_available,
        }
