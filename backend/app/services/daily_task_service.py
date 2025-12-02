"""Daily task service for managing daily tasks."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask, TaskStatus
from app.schemas import DailyTaskCreate, DailyTaskUpdate, DailyTaskReorderRequest


class DailyTaskService:
    def __init__(self, db: Session):
        self.db = db

    def _get_roadmap_service(self):
        """Lazy import to avoid circular dependency."""
        from app.services.roadmap_service import RoadmapService
        return RoadmapService(self.db)

    def toggle_daily_task(self, task_id: UUID, user_id: UUID) -> DailyTask:
        """Toggle daily task completion status."""
        task = (
            self.db.query(DailyTask)
            .join(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(DailyTask.id == task_id, Roadmap.user_id == user_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily task not found",
            )

        # Toggle check status
        task.is_checked = not task.is_checked
        task.status = TaskStatus.COMPLETED if task.is_checked else TaskStatus.PENDING

        self.db.commit()
        self.db.refresh(task)

        # Update parent progress
        self._update_weekly_progress(task.weekly_task_id)

        return task

    def _update_weekly_progress(self, weekly_task_id: UUID):
        """Update weekly task progress based on daily tasks."""
        weekly = self.db.query(WeeklyTask).filter(WeeklyTask.id == weekly_task_id).first()
        if not weekly:
            return

        total = len(weekly.daily_tasks)
        completed = sum(1 for d in weekly.daily_tasks if d.is_checked)

        weekly.progress = int((completed / total) * 100) if total > 0 else 0
        weekly.status = TaskStatus.COMPLETED if weekly.progress == 100 else (
            TaskStatus.IN_PROGRESS if weekly.progress > 0 else TaskStatus.PENDING
        )

        self.db.commit()
        self._update_monthly_progress(weekly.monthly_goal_id)

    def _update_monthly_progress(self, monthly_goal_id: UUID):
        """Update monthly goal progress based on weekly tasks."""
        monthly = self.db.query(MonthlyGoal).filter(MonthlyGoal.id == monthly_goal_id).first()
        if not monthly:
            return

        total = len(monthly.weekly_tasks)
        progress_sum = sum(w.progress for w in monthly.weekly_tasks)

        monthly.progress = int(progress_sum / total) if total > 0 else 0
        monthly.status = TaskStatus.COMPLETED if monthly.progress == 100 else (
            TaskStatus.IN_PROGRESS if monthly.progress > 0 else TaskStatus.PENDING
        )

        self.db.commit()

        # Update roadmap progress
        roadmap_service = self._get_roadmap_service()
        roadmap_service.update_progress(monthly.roadmap_id)

    def create_daily_task(
        self, weekly_task_id: UUID, user_id: UUID, data: DailyTaskCreate
    ) -> DailyTask:
        """Create a new daily task."""
        # Verify ownership
        weekly = (
            self.db.query(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(WeeklyTask.id == weekly_task_id, Roadmap.user_id == user_id)
            .first()
        )
        if not weekly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly task not found",
            )

        # Get max order for this day
        max_order = (
            self.db.query(DailyTask)
            .filter(
                DailyTask.weekly_task_id == weekly_task_id,
                DailyTask.day_number == data.day_number,
            )
            .count()
        )

        task = DailyTask(
            weekly_task_id=weekly_task_id,
            day_number=data.day_number,
            order=data.order if data.order is not None else max_order,
            title=data.title,
            description=data.description,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Increment edit count if finalized
        monthly = weekly.monthly_goal
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(monthly.roadmap_id)

        return task

    def update_daily_task(
        self, task_id: UUID, user_id: UUID, data: DailyTaskUpdate
    ) -> DailyTask:
        """Update a daily task."""
        task = (
            self.db.query(DailyTask)
            .join(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(DailyTask.id == task_id, Roadmap.user_id == user_id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily task not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)

        # Increment edit count if finalized
        roadmap_id = task.weekly_task.monthly_goal.roadmap_id
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(roadmap_id)

        return task

    def delete_daily_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a daily task."""
        task = (
            self.db.query(DailyTask)
            .join(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(DailyTask.id == task_id, Roadmap.user_id == user_id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily task not found",
            )

        # Store for progress update
        weekly_task_id = task.weekly_task_id
        roadmap_id = task.weekly_task.monthly_goal.roadmap_id

        self.db.delete(task)
        self.db.commit()

        # Update progress
        self._update_weekly_progress(weekly_task_id)

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(roadmap_id)

        return True

    def reorder_daily_tasks(
        self, data: DailyTaskReorderRequest, user_id: UUID
    ) -> List[DailyTask]:
        """Reorder daily tasks."""
        updated_tasks = []
        for item in data.tasks:
            task = (
                self.db.query(DailyTask)
                .join(WeeklyTask)
                .join(MonthlyGoal)
                .join(Roadmap)
                .filter(DailyTask.id == item.task_id, Roadmap.user_id == user_id)
                .first()
            )
            if task:
                task.order = item.new_order
                updated_tasks.append(task)

        self.db.commit()
        for task in updated_tasks:
            self.db.refresh(task)

        return updated_tasks
