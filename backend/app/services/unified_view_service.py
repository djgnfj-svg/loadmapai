"""Unified view service for aggregating tasks across multiple roadmaps."""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session, joinedload

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask
from app.models.roadmap import RoadmapStatus


class UnifiedViewService:
    """Service for unified view that aggregates tasks from multiple roadmaps."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_task_date(
        self,
        roadmap_start_date: date,
        month_number: int,
        week_number: int,
        day_number: int,
    ) -> date:
        """
        Calculate the actual date for a daily task based on relative positions.

        Args:
            roadmap_start_date: The start date of the roadmap
            month_number: Month number (1-based, e.g., 1, 2, 3...)
            week_number: Week number within the month (1-4)
            day_number: Day number within the week (1-7)

        Returns:
            The actual calendar date for this task
        """
        # Start from roadmap start date
        # Add (month_number - 1) months
        task_date = roadmap_start_date + relativedelta(months=month_number - 1)

        # Add (week_number - 1) weeks
        task_date = task_date + timedelta(weeks=week_number - 1)

        # Add (day_number - 1) days
        task_date = task_date + timedelta(days=day_number - 1)

        return task_date

    def _get_active_roadmaps_with_tasks(
        self, user_id: UUID, date_start: date, date_end: date
    ) -> List[Roadmap]:
        """Get all active roadmaps that overlap with the given date range."""
        return (
            self.db.query(Roadmap)
            .options(
                joinedload(Roadmap.monthly_goals)
                .joinedload(MonthlyGoal.weekly_tasks)
                .joinedload(WeeklyTask.daily_tasks)
            )
            .filter(
                Roadmap.user_id == user_id,
                Roadmap.status == RoadmapStatus.ACTIVE,
                Roadmap.start_date <= date_end,
                Roadmap.end_date >= date_start,
            )
            .all()
        )

    def get_today_tasks(
        self, user_id: UUID, target_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all daily tasks for today (or specified date) across all active roadmaps.

        Args:
            user_id: The user's ID
            target_date: The date to get tasks for (defaults to today)

        Returns:
            List of task dictionaries with roadmap context
        """
        if target_date is None:
            target_date = date.today()

        roadmaps = self._get_active_roadmaps_with_tasks(user_id, target_date, target_date)
        today_tasks = []

        for roadmap in roadmaps:
            for monthly in roadmap.monthly_goals:
                for weekly in monthly.weekly_tasks:
                    for daily in weekly.daily_tasks:
                        task_date = self.calculate_task_date(
                            roadmap.start_date,
                            monthly.month_number,
                            weekly.week_number,
                            daily.day_number,
                        )

                        if task_date == target_date:
                            today_tasks.append(
                                {
                                    "task": daily,
                                    "roadmap": roadmap,
                                    "monthly_goal": monthly,
                                    "weekly_task": weekly,
                                    "actual_date": task_date,
                                }
                            )

        # Sort by roadmap title, then by order
        today_tasks.sort(key=lambda x: (x["roadmap"].title, x["task"].order))
        return today_tasks

    def get_current_week_tasks(
        self, user_id: UUID, target_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get current week's weekly tasks and their daily tasks across all active roadmaps.

        Args:
            user_id: The user's ID
            target_date: A date within the target week (defaults to today)

        Returns:
            List of weekly task dictionaries with daily tasks and roadmap context
        """
        if target_date is None:
            target_date = date.today()

        # Calculate week boundaries (Monday to Sunday)
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)

        roadmaps = self._get_active_roadmaps_with_tasks(user_id, week_start, week_end)
        weekly_data = []

        for roadmap in roadmaps:
            for monthly in roadmap.monthly_goals:
                for weekly in monthly.weekly_tasks:
                    # Calculate this weekly task's date range
                    week_task_start = self.calculate_task_date(
                        roadmap.start_date,
                        monthly.month_number,
                        weekly.week_number,
                        1,  # First day of the week
                    )
                    week_task_end = self.calculate_task_date(
                        roadmap.start_date,
                        monthly.month_number,
                        weekly.week_number,
                        7,  # Last day of the week
                    )

                    # Check if this weekly task overlaps with current week
                    if week_task_start <= week_end and week_task_end >= week_start:
                        daily_tasks_with_dates = [
                            {
                                "task": dt,
                                "actual_date": self.calculate_task_date(
                                    roadmap.start_date,
                                    monthly.month_number,
                                    weekly.week_number,
                                    dt.day_number,
                                ),
                            }
                            for dt in sorted(weekly.daily_tasks, key=lambda x: (x.day_number, x.order))
                        ]

                        weekly_data.append(
                            {
                                "weekly_task": weekly,
                                "roadmap": roadmap,
                                "monthly_goal": monthly,
                                "week_start": week_task_start,
                                "week_end": week_task_end,
                                "daily_tasks": daily_tasks_with_dates,
                            }
                        )

        # Sort by roadmap title
        weekly_data.sort(key=lambda x: x["roadmap"].title)
        return weekly_data

    def get_unified_view(
        self, user_id: UUID, target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get unified view data combining today's tasks and current week's goals.

        Args:
            user_id: The user's ID
            target_date: The target date (defaults to today)

        Returns:
            Dictionary containing today_tasks and current_week data
        """
        if target_date is None:
            target_date = date.today()

        return {
            "target_date": target_date,
            "today_tasks": self.get_today_tasks(user_id, target_date),
            "current_week": self.get_current_week_tasks(user_id, target_date),
        }
