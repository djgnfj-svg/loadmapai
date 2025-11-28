from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask, TaskStatus
from app.schemas import (
    RoadmapCreate, RoadmapUpdate, RoadmapScheduleUpdate,
    MonthlyGoalCreate, MonthlyGoalUpdate,
    WeeklyTaskCreate, WeeklyTaskUpdate,
    DailyTaskCreate, DailyTaskUpdate, DailyTaskReorderRequest,
)


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

    def finalize_roadmap(self, roadmap_id: UUID, user_id: UUID) -> Roadmap:
        """확정: 로드맵을 확정 상태로 변경"""
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
        """확정 해제: 로드맵 확정 상태 해제"""
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
        """스케줄 설정 업데이트"""
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
        """확정 후 수정 횟수 증가"""
        roadmap = self.db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
        if roadmap and roadmap.is_finalized:
            roadmap.edit_count_after_finalize += 1
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

    def create_daily_task(
        self, weekly_task_id: UUID, user_id: UUID, data: DailyTaskCreate
    ) -> DailyTask:
        """일일 태스크 생성"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(monthly.roadmap_id)

        return task

    def update_daily_task(
        self, task_id: UUID, user_id: UUID, data: DailyTaskUpdate
    ) -> DailyTask:
        """일일 태스크 수정"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(roadmap_id)

        return task

    def delete_daily_task(self, task_id: UUID, user_id: UUID) -> bool:
        """일일 태스크 삭제"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(roadmap_id)

        return True

    def reorder_daily_tasks(
        self, data: DailyTaskReorderRequest, user_id: UUID
    ) -> List[DailyTask]:
        """일일 태스크 순서 변경"""
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


class MonthlyGoalService:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_goal(self, goal_id: UUID, user_id: UUID) -> Optional[MonthlyGoal]:
        return (
            self.db.query(MonthlyGoal)
            .join(Roadmap)
            .filter(MonthlyGoal.id == goal_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_monthly_goal(
        self, roadmap_id: UUID, user_id: UUID, data: MonthlyGoalCreate
    ) -> MonthlyGoal:
        """월별 목표 생성"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(roadmap_id)

        return goal

    def update_monthly_goal(
        self, goal_id: UUID, user_id: UUID, data: MonthlyGoalUpdate
    ) -> MonthlyGoal:
        """월별 목표 수정"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(goal.roadmap_id)

        return goal

    def delete_monthly_goal(self, goal_id: UUID, user_id: UUID) -> bool:
        """월별 목표 삭제"""
        goal = self.get_monthly_goal(goal_id, user_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monthly goal not found",
            )

        roadmap_id = goal.roadmap_id
        self.db.delete(goal)
        self.db.commit()

        # Increment edit count if finalized
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(roadmap_id)
        roadmap_service.update_progress(roadmap_id)

        return True


class WeeklyTaskService:
    def __init__(self, db: Session):
        self.db = db

    def get_weekly_task(self, task_id: UUID, user_id: UUID) -> Optional[WeeklyTask]:
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
        """주간 태스크 생성"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(monthly.roadmap_id)

        return task

    def update_weekly_task(
        self, task_id: UUID, user_id: UUID, data: WeeklyTaskUpdate
    ) -> WeeklyTask:
        """주간 태스크 수정"""
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
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(task.monthly_goal.roadmap_id)

        return task

    def delete_weekly_task(self, task_id: UUID, user_id: UUID) -> bool:
        """주간 태스크 삭제"""
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

        # Update progress
        monthly = self.db.query(MonthlyGoal).filter(MonthlyGoal.id == monthly_goal_id).first()
        if monthly:
            total = len(monthly.weekly_tasks)
            progress_sum = sum(w.progress for w in monthly.weekly_tasks)
            monthly.progress = int(progress_sum / total) if total > 0 else 0
            self.db.commit()

        # Increment edit count if finalized
        roadmap_service = RoadmapService(self.db)
        roadmap_service.increment_edit_count(roadmap_id)
        roadmap_service.update_progress(roadmap_id)

        return True
