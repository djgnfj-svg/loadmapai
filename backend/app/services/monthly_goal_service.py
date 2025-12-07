"""Monthly goal service for managing monthly goals."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID

from app.models import Roadmap, MonthlyGoal
from app.schemas import MonthlyGoalCreate, MonthlyGoalUpdate


class MonthlyGoalService:
    def __init__(self, db: Session):
        self.db = db

    def _get_roadmap_service(self):
        """Lazy import to avoid circular dependency."""
        from app.services.roadmap_service import RoadmapService
        return RoadmapService(self.db)

    def get_monthly_goal(self, goal_id: UUID, user_id: UUID) -> Optional[MonthlyGoal]:
        """Get a monthly goal by ID with ownership verification."""
        return (
            self.db.query(MonthlyGoal)
            .join(Roadmap)
            .filter(MonthlyGoal.id == goal_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_monthly_goal(
        self, roadmap_id: UUID, user_id: UUID, data: MonthlyGoalCreate
    ) -> MonthlyGoal:
        """Create a new monthly goal."""
        roadmap = (
            self.db.query(Roadmap)
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found",
            )

        goal = MonthlyGoal(
            roadmap_id=roadmap_id,
            month_number=data.month_number,
            title=data.title,
            description=data.description,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(roadmap_id)

        return goal

    def update_monthly_goal(
        self, goal_id: UUID, user_id: UUID, data: MonthlyGoalUpdate
    ) -> MonthlyGoal:
        """Update a monthly goal."""
        goal = self.get_monthly_goal(goal_id, user_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monthly goal not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        self.db.commit()
        self.db.refresh(goal)

        # Increment edit count if finalized
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(goal.roadmap_id)

        return goal

    def delete_monthly_goal(self, goal_id: UUID, user_id: UUID) -> bool:
        """Delete a monthly goal."""
        goal = self.get_monthly_goal(goal_id, user_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monthly goal not found",
            )

        roadmap_id = goal.roadmap_id
        self.db.delete(goal)
        self.db.commit()

        # Increment edit count if finalized and update progress
        roadmap_service = self._get_roadmap_service()
        roadmap_service.increment_edit_count(roadmap_id)
        roadmap_service.update_progress(roadmap_id)

        return True
