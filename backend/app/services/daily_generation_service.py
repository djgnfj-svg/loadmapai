"""Service for generating daily tasks for a specific week (lazy generation)."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyGoal, DailyTask
from app.ai.llm import invoke_llm_json
from app.ai.prompts.templates import SINGLE_WEEK_DAILY_TASKS_PROMPT, build_interview_section


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
        """Synchronously generate daily tasks using LLM."""
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
        except Exception as e:
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

    def _save_daily_tasks(self, weekly_task_id: UUID, days: list[dict]):
        """Save generated daily tasks to database."""
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

            # Save daily tasks
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
