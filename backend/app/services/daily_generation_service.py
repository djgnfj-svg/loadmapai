"""Service for generating daily tasks for a specific week (lazy generation)."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyGoal, DailyTask, RoadmapMode
from app.models.question import Question, QuestionType
from app.ai.llm import invoke_llm_json
from app.ai.prompts.templates import SINGLE_WEEK_DAILY_TASKS_PROMPT, build_interview_section
from app.ai.prompts.learning_templates import (
    LEARNING_DAILY_QUESTIONS_PROMPT,
    calculate_intensity,
    get_weekend_intensity,
)


_executor = ThreadPoolExecutor(max_workers=2)


class DailyGenerationService:
    def __init__(self, db: Session):
        self.db = db

    def get_weekly_task_with_context(
        self, weekly_task_id: UUID, user_id: UUID
    ) -> tuple[WeeklyTask, Roadmap]:
        """Get weekly task with roadmap context."""
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

    def has_daily_tasks(self, weekly_task_id: UUID) -> bool:
        """Check if weekly task already has daily tasks."""
        count = (
            self.db.query(DailyTask)
            .filter(DailyTask.weekly_task_id == weekly_task_id)
            .count()
        )
        return count > 0

    def is_previous_week_completed(self, weekly_task: WeeklyTask) -> bool:
        """Check if the previous week is completed (100% progress).

        First week of first month is always considered ready.
        """
        month_number = weekly_task.monthly_goal.month_number
        week_number = weekly_task.week_number
        roadmap_id = weekly_task.monthly_goal.roadmap_id

        # First week of first month is always ready
        if month_number == 1 and week_number == 1:
            return True

        # Find previous week
        if week_number > 1:
            # Previous week in same month
            prev_week = (
                self.db.query(WeeklyTask)
                .join(MonthlyGoal)
                .filter(
                    MonthlyGoal.roadmap_id == roadmap_id,
                    MonthlyGoal.month_number == month_number,
                    WeeklyTask.week_number == week_number - 1,
                )
                .first()
            )
        else:
            # Last week of previous month
            prev_week = (
                self.db.query(WeeklyTask)
                .join(MonthlyGoal)
                .filter(
                    MonthlyGoal.roadmap_id == roadmap_id,
                    MonthlyGoal.month_number == month_number - 1,
                    WeeklyTask.week_number == 4,
                )
                .first()
            )

        if not prev_week:
            return True  # No previous week found, allow generation

        return prev_week.progress == 100

    def get_next_week(self, weekly_task: WeeklyTask) -> WeeklyTask | None:
        """Get the next week after the given week."""
        month_number = weekly_task.monthly_goal.month_number
        week_number = weekly_task.week_number
        roadmap_id = weekly_task.monthly_goal.roadmap_id

        if week_number < 4:
            # Next week in same month
            return (
                self.db.query(WeeklyTask)
                .join(MonthlyGoal)
                .filter(
                    MonthlyGoal.roadmap_id == roadmap_id,
                    MonthlyGoal.month_number == month_number,
                    WeeklyTask.week_number == week_number + 1,
                )
                .first()
            )
        else:
            # First week of next month
            return (
                self.db.query(WeeklyTask)
                .join(MonthlyGoal)
                .filter(
                    MonthlyGoal.roadmap_id == roadmap_id,
                    MonthlyGoal.month_number == month_number + 1,
                    WeeklyTask.week_number == 1,
                )
                .first()
            )

    def _generate_daily_tasks_sync(
        self,
        weekly_task: WeeklyTask,
        roadmap: Roadmap,
        interview_context: dict | None = None,
    ) -> list[dict]:
        """Synchronously generate daily tasks using LLM.

        Routes to different generation methods based on roadmap mode:
        - PLANNING mode: Generates checklist-style tasks
        - LEARNING mode: Generates questions for each day
        """
        # Check mode and route accordingly
        if roadmap.mode == RoadmapMode.LEARNING:
            return self._generate_learning_days_sync(
                weekly_task, roadmap, interview_context
            )

        # PLANNING mode (default)
        return self._generate_planning_days_sync(
            weekly_task, roadmap, interview_context
        )

    def _generate_planning_days_sync(
        self,
        weekly_task: WeeklyTask,
        roadmap: Roadmap,
        interview_context: dict | None = None,
    ) -> list[dict]:
        """Generate PLANNING mode daily tasks (checklist-style)."""
        interview_section = build_interview_section(interview_context or {})

        prompt = SINGLE_WEEK_DAILY_TASKS_PROMPT.format(
            topic=roadmap.topic,
            interview_section=interview_section,
            week_title=weekly_task.title,
            week_description=weekly_task.description or "",
            month_number=weekly_task.monthly_goal.month_number,
            week_number=weekly_task.week_number,
        )

        try:
            result = invoke_llm_json(prompt, temperature=0.7)
            return result.get("days", [])
        except Exception:
            # Fallback: generate basic daily tasks
            return [
                {
                    "day_number": d + 1,
                    "goal": {
                        "title": f"{d + 1}일차 학습",
                        "description": f"{weekly_task.title} 관련 학습"
                    },
                    "tasks": [
                        {"title": "이론 학습", "description": f"{weekly_task.title} 개념 학습"},
                        {"title": "실습", "description": f"{weekly_task.title} 실습 과제"},
                    ] if d < 5 else [
                        {"title": "복습", "description": "이번 주 학습 내용 복습"},
                    ]
                }
                for d in range(7)
            ]

    def _generate_learning_days_sync(
        self,
        weekly_task: WeeklyTask,
        roadmap: Roadmap,
        interview_context: dict | None = None,
    ) -> list[dict]:
        """Generate LEARNING mode daily tasks with questions."""
        interview_section = build_interview_section(interview_context or {})

        # Generate 7 days, each with questions
        days = []
        for day_num in range(1, 8):
            day_data = self._generate_day_questions_sync(
                weekly_task=weekly_task,
                roadmap=roadmap,
                day_number=day_num,
                interview_section=interview_section,
            )
            days.append(day_data)

        return days

    def _generate_day_questions_sync(
        self,
        weekly_task: WeeklyTask,
        roadmap: Roadmap,
        day_number: int,
        interview_section: str,
    ) -> dict:
        """Generate questions for a single day in LEARNING mode."""
        # Calculate intensity based on topic and duration
        base_intensity, base_question_count = calculate_intensity(
            roadmap.topic, roadmap.duration_months
        )

        # Determine daily topic based on day number and week content
        daily_title = f"{day_number}일차: {weekly_task.title} 학습"
        daily_description = f"{weekly_task.title}의 {day_number}일차 학습 내용"

        # For weekends (day 6-7), use lighter intensity for review
        if day_number >= 6:
            daily_title = f"{day_number}일차: 복습 및 정리"
            daily_description = f"이번 주 {weekly_task.title} 학습 내용 복습"
            intensity, question_count = get_weekend_intensity(base_intensity)
        else:
            intensity = base_intensity
            question_count = base_question_count

        prompt = LEARNING_DAILY_QUESTIONS_PROMPT.format(
            topic=roadmap.topic,
            duration_months=roadmap.duration_months,
            intensity=intensity,
            question_count=question_count,
            month_number=weekly_task.monthly_goal.month_number,
            week_number=weekly_task.week_number,
            day_number=day_number,
            daily_title=daily_title,
            daily_description=daily_description,
            weekly_title=weekly_task.title,
            weekly_description=weekly_task.description or "",
            interview_section=interview_section,
        )

        try:
            result = invoke_llm_json(prompt, temperature=0.7)
            questions = result.get("questions", [])

            return {
                "day_number": day_number,
                "goal": {
                    "title": daily_title,
                    "description": daily_description,
                },
                "tasks": [],  # No traditional tasks in LEARNING mode
                "questions": questions,  # Questions instead
            }
        except Exception:
            # Fallback: generate basic questions
            return {
                "day_number": day_number,
                "goal": {
                    "title": daily_title,
                    "description": daily_description,
                },
                "tasks": [],
                "questions": [
                    {
                        "question_type": "MULTIPLE_CHOICE",
                        "question_text": f"{weekly_task.title}에 대한 기본 개념 문제입니다.",
                        "choices": ["선택지 A", "선택지 B", "선택지 C", "선택지 D"],
                        "correct_answer": "0",
                        "hint": "기본 개념을 떠올려보세요.",
                        "explanation": "정답 해설입니다.",
                    },
                    {
                        "question_type": "SHORT_ANSWER",
                        "question_text": f"{weekly_task.title}의 핵심 용어를 작성하세요.",
                        "correct_answer": "핵심 용어",
                        "hint": "수업에서 배운 중요한 용어입니다.",
                        "explanation": "해당 용어는 학습 내용의 핵심입니다.",
                    },
                    {
                        "question_type": "ESSAY",
                        "question_text": f"{weekly_task.title}의 주요 개념을 설명하세요.",
                        "correct_answer": "주요 개념에 대한 설명으로 핵심 키워드들이 포함되어야 합니다.",
                        "hint": "배운 내용을 자신의 말로 정리해보세요.",
                        "explanation": "개념 이해도를 확인하는 문제입니다.",
                    },
                ],
            }

    def _save_daily_tasks(self, weekly_task_id: UUID, days: list[dict]):
        """Save generated daily tasks to database.

        Handles both PLANNING mode (tasks) and LEARNING mode (questions).
        """
        for day_data in days:
            # Save daily goal if present
            goal_data = day_data.get("goal")
            if goal_data:
                daily_goal = DailyGoal(
                    weekly_task_id=weekly_task_id,
                    day_number=day_data["day_number"],
                    title=goal_data.get("title", f"{day_data['day_number']}일차"),
                    description=goal_data.get("description", ""),
                )
                self.db.add(daily_goal)

            # Check if this is LEARNING mode (has questions) or PLANNING mode (has tasks)
            questions = day_data.get("questions", [])

            if questions:
                # LEARNING mode: Create a single daily task and save questions
                daily_task = DailyTask(
                    weekly_task_id=weekly_task_id,
                    day_number=day_data["day_number"],
                    order=0,
                    title=goal_data.get("title", f"{day_data['day_number']}일차 학습") if goal_data else f"{day_data['day_number']}일차 학습",
                    description=goal_data.get("description", "") if goal_data else "",
                )
                self.db.add(daily_task)
                self.db.flush()  # Get the daily_task.id

                # Save questions
                for order, q in enumerate(questions):
                    question = Question(
                        daily_task_id=daily_task.id,
                        question_type=QuestionType(q.get("question_type", "SHORT_ANSWER")),
                        question_text=q["question_text"],
                        choices=q.get("choices"),
                        correct_answer=q["correct_answer"],
                        hint=q.get("hint"),
                        explanation=q.get("explanation"),
                        order=order,
                    )
                    self.db.add(question)
            else:
                # PLANNING mode: Save multiple daily tasks
                tasks = day_data.get("tasks", [])
                for order, task in enumerate(tasks):
                    daily_task = DailyTask(
                        weekly_task_id=weekly_task_id,
                        day_number=day_data["day_number"],
                        order=order,
                        title=task["title"],
                        description=task.get("description", ""),
                    )
                    self.db.add(daily_task)

        self.db.commit()

    async def generate_daily_tasks_for_week(
        self,
        weekly_task_id: UUID,
        user_id: UUID,
        force: bool = False,
        interview_context: dict | None = None,
    ) -> WeeklyTask:
        """Generate daily tasks for a specific week.

        Args:
            weekly_task_id: The weekly task ID
            user_id: The user ID for ownership verification
            force: If True, skip previous week completion check
            interview_context: Optional interview context for personalization

        Returns:
            The updated weekly task with daily tasks
        """
        weekly_task, roadmap = self.get_weekly_task_with_context(weekly_task_id, user_id)

        # Check if already has daily tasks
        if self.has_daily_tasks(weekly_task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 주차는 이미 일일 태스크가 생성되어 있습니다.",
            )

        # Check if previous week is completed (unless force=True)
        if not force and not self.is_previous_week_completed(weekly_task):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이전 주차를 먼저 완료해야 합니다.",
            )

        # Generate daily tasks in thread pool
        loop = asyncio.get_event_loop()
        days = await loop.run_in_executor(
            _executor,
            self._generate_daily_tasks_sync,
            weekly_task,
            roadmap,
            interview_context,
        )

        # Save to database
        self._save_daily_tasks(weekly_task_id, days)

        # Refresh and return
        self.db.refresh(weekly_task)
        return weekly_task

    async def try_generate_next_week(
        self,
        current_weekly_task_id: UUID,
        user_id: UUID,
    ) -> WeeklyTask | None:
        """Try to generate daily tasks for the next week if current week is completed.

        This is called after a task is toggled. If the current week reaches 100%,
        it will automatically generate daily tasks for the next week.

        Returns:
            The next weekly task with generated daily tasks, or None if not applicable
        """
        weekly_task, _ = self.get_weekly_task_with_context(current_weekly_task_id, user_id)

        # Check if current week is completed
        if weekly_task.progress != 100:
            return None

        # Get next week
        next_week = self.get_next_week(weekly_task)
        if not next_week:
            return None

        # Check if next week already has daily tasks
        if self.has_daily_tasks(next_week.id):
            return None

        # Generate daily tasks for next week
        return await self.generate_daily_tasks_for_week(
            next_week.id, user_id, force=True
        )
