"""Roadmap service for managing roadmaps."""
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyGoal, DailyTask
from app.schemas import RoadmapCreate, RoadmapUpdate, RoadmapScheduleUpdate


class RoadmapService:
    def __init__(self, db: Session):
        self.db = db

    def get_roadmaps(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Roadmap]:
        """Get all roadmaps for a user."""
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.user_id == user_id)
            .order_by(Roadmap.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_roadmap(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        """Get a roadmap by ID with ownership verification."""
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def get_roadmap_with_monthly(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        """Get roadmap with monthly goals eagerly loaded."""
        return (
            self.db.query(Roadmap)
            .options(joinedload(Roadmap.monthly_goals))
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def get_roadmap_full(self, roadmap_id: UUID, user_id: UUID) -> Optional[Roadmap]:
        """Get roadmap with all nested data eagerly loaded."""
        return (
            self.db.query(Roadmap)
            .options(
                joinedload(Roadmap.monthly_goals)
                .joinedload(MonthlyGoal.weekly_tasks)
                .joinedload(WeeklyTask.daily_goals),
                joinedload(Roadmap.monthly_goals)
                .joinedload(MonthlyGoal.weekly_tasks)
                .joinedload(WeeklyTask.daily_tasks)
            )
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_roadmap(self, user_id: UUID, data: RoadmapCreate) -> Roadmap:
        """Create a new roadmap."""
        # Calculate end date using relativedelta for accuracy
        end_date = data.start_date + relativedelta(months=data.duration_months)

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
        """Update a roadmap."""
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
        """Delete a roadmap."""
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
        """Recalculate and update roadmap progress based on daily tasks.

        Optimized with eager loading to avoid N+1 query problem.
        """
        # Eager load all related data in a single query
        roadmap = (
            self.db.query(Roadmap)
            .options(
                joinedload(Roadmap.monthly_goals)
                .joinedload(MonthlyGoal.weekly_tasks)
                .joinedload(WeeklyTask.daily_tasks)
            )
            .filter(Roadmap.id == roadmap_id)
            .first()
        )
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

    def finalize_roadmap(self, roadmap_id: UUID, user_id: UUID) -> Roadmap:
        """Finalize a roadmap."""
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found",
            )

        if roadmap.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="로드맵이 이미 확정되어 있습니다.",
            )

        roadmap.is_finalized = True
        roadmap.finalized_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def unfinalize_roadmap(self, roadmap_id: UUID, user_id: UUID) -> Roadmap:
        """Unfinalize a roadmap."""
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found",
            )

        if not roadmap.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="로드맵이 아직 확정되지 않았습니다.",
            )

        roadmap.is_finalized = False
        roadmap.finalized_at = None
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def update_schedule(
        self, roadmap_id: UUID, user_id: UUID, data: RoadmapScheduleUpdate
    ) -> Roadmap:
        """Update roadmap schedule settings."""
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

    def increment_edit_count(self, roadmap_id: UUID):
        """Increment edit count after finalization."""
        roadmap = self.db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
        if roadmap and roadmap.is_finalized:
            roadmap.edit_count_after_finalize += 1
            self.db.commit()