"""Weekly task service for managing weekly tasks."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID

from app.models import Roadmap, MonthlyGoal, WeeklyTask, TaskStatus
from app.schemas import WeeklyTaskCreate, WeeklyTaskUpdate


class WeeklyTaskService:
    def __init__(self, db: Session):
        self.db = db

    def _get_roadmap_service(self):
        """Lazy import to avoid circular dependency."""
        from app.services.roadmap_service import RoadmapService
        return RoadmapService(self.db)

    def get_weekly_task(self, task_id: UUID, user_id: UUID) -> Optional[WeeklyTask]:
        """Get a weekly task by ID with ownership verification."""
        return (
            self.db.query(WeeklyTask)
            .join(MonthlyGoal)
            .join(Roadmap)
            .filter(WeeklyTask.id == task_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_weekly_task(
        self, monthly_goal_id: UUID, user_id: UUID, data: WeeklyTaskCreate
    ) -> WeeklyTask:
        """Create a new weekly task."""
        monthly = (
            self.db.query(MonthlyGoal)
            .join(Roadmap)
            .filter(MonthlyGoal.id == monthly_goal_id, Roadmap.user_id == user_id)
            .first()
        )
        if not monthly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monthly goal not found",
            )

        task = WeeklyTask(
            monthly_goal_id=monthly_goal_id,
            week_number=data.week_number,
            title=data.title,
            description=data.description,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(monthly.roadmap_id)

        return task

    def update_weekly_task(
        self, task_id: UUID, user_id: UUID, data: WeeklyTaskUpdate
    ) -> WeeklyTask:
        """Update a weekly task."""
        task = self.get_weekly_task(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly task not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(task.monthly_goal.roadmap_id)

        return task

    def delete_weekly_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a weekly task."""
        task = self.get_weekly_task(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly task not found",
            )

        roadmap_id = task.monthly_goal.roadmap_id
        monthly_goal_id = task.monthly_goal_id
        self.db.delete(task)
        self.db.commit()

        # Update monthly progress
        monthly = self.db.query(MonthlyGoal).filter(MonthlyGoal.id == monthly_goal_id).first()
        if monthly:
            total = len(monthly.weekly_tasks)
            progress_sum = sum(w.progress for w in monthly.weekly_tasks)
            monthly.progress = int(progress_sum / total) if total > 0 else 0
            monthly.status = TaskStatus.COMPLETED if monthly.progress == 100 else (
                TaskStatus.IN_PROGRESS if monthly.progress > 0 else TaskStatus.PENDING
            )
            self.db.commit()

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(roadmap_id)
        roadmap_service.update_progress(roadmap_id)

        return True
