from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import timedelta

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask, TaskStatus
from app.schemas import RoadmapCreate, RoadmapUpdate


class RoadmapService:
    def __init__(self, db: Session):
        self.db = db

    def get_roadmaps(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Roadmap]:
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.user_id == user_id)
            .order_by(Roadmap.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_roadmap(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def get_roadmap_with_monthly(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        return (
            self.db.query(Roadmap)
            .options(joinedload(Roadmap.monthly_goals))
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def get_roadmap_full(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        return (
            self.db.query(Roadmap)
            .options(
                joinedload(Roadmap.monthly_goals)
                .joinedload(MonthlyGoal.weekly_tasks)
                .joinedload(WeeklyTask.daily_tasks)
            )
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_roadmap(self, user_id: UUID, data: RoadmapCreate) -> Roadmap:
        # Calculate end date
        end_date = data.start_date + timedelta(days=data.duration_months * 30)

        roadmap = Roadmap(
            user_id=user_id,
            title=f"{data.topic} 학습 로드맵",
            topic=data.topic,
            duration_months=data.duration_months,
            start_date=data.start_date,
            end_date=end_date,
            mode=data.mode,
        )
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def update_roadmap(
        self, roadmap_id: UUID, user_id: UUID, data: RoadmapUpdate
    ) -> Roadmap:
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(roadmap, field, value)

        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def delete_roadmap(self, roadmap_id: UUID, user_id: UUID) -> bool:
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found",
            )

        self.db.delete(roadmap)
        self.db.commit()
        return True

    def update_progress(self, roadmap_id: UUID):
        """Recalculate and update roadmap progress based on daily tasks."""
        roadmap = self.db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
        if not roadmap:
            return

        total_tasks = 0
        completed_tasks = 0

        for monthly in roadmap.monthly_goals:
            for weekly in monthly.weekly_tasks:
                for daily in weekly.daily_tasks:
                    total_tasks += 1
                    if daily.is_checked:
                        completed_tasks += 1

        if total_tasks > 0:
            roadmap.progress = int((completed_tasks / total_tasks) * 100)
            self.db.commit()


class DailyTaskService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_task(self, task_id: UUID) -> Optional[DailyTask]:
        return self.db.query(DailyTask).filter(DailyTask.id == task_id).first()

    def toggle_daily_task(self, task_id: UUID, user_id: UUID) -> DailyTask:
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.update_progress(monthly.roadmap_id)
