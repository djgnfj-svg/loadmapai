"""Saver node - saves generated roadmap to database."""
from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask
from app.ai.state import RoadmapGenerationState


def save_roadmap(state: RoadmapGenerationState, db: Session) -> RoadmapGenerationState:
    """Save the generated roadmap to the database.

    Data structure:
    - monthly_goals: [{month_number, title, description}, ...]
    - weekly_tasks: [{month_number, weeks: [{week_number, title, description}, ...]}, ...]
    - daily_tasks: [{month_number, week_number, days: [{day_number, title, description}, ...]}, ...]
    """
    # Calculate end date
    end_date = state["start_date"] + timedelta(days=state["duration_months"] * 30)

    # Create roadmap
    roadmap = Roadmap(
        user_id=UUID(state["user_id"]),
        title=state["title"],
        description=state["description"],
        topic=state["topic"],
        duration_months=state["duration_months"],
        start_date=state["start_date"],
        end_date=end_date,
        mode=state["mode"],
    )
    db.add(roadmap)
    db.flush()

    # Create monthly goals
    for monthly_data in state["monthly_goals"]:
        monthly_goal = MonthlyGoal(
            roadmap_id=roadmap.id,
            month_number=monthly_data["month_number"],
            title=monthly_data["title"],
            description=monthly_data["description"],
        )
        db.add(monthly_goal)
        db.flush()

        # Find weekly tasks for this month
        weekly_month = next(
            (w for w in state["weekly_tasks"] if w["month_number"] == monthly_data["month_number"]),
            None
        )

        if weekly_month and "weeks" in weekly_month:
            for week_data in weekly_month["weeks"]:
                weekly_task = WeeklyTask(
                    monthly_goal_id=monthly_goal.id,
                    week_number=week_data["week_number"],
                    title=week_data["title"],
                    description=week_data["description"],
                )
                db.add(weekly_task)
                db.flush()

                # Find daily tasks for this week
                daily_week = next(
                    (d for d in state["daily_tasks"]
                     if d["month_number"] == monthly_data["month_number"]
                     and d["week_number"] == week_data["week_number"]),
                    None
                )

                if daily_week and "days" in daily_week:
                    for day_data in daily_week["days"]:
                        tasks = day_data.get("tasks", [])
                        # 기존 형식 호환 (tasks 배열 없이 title/description만 있는 경우)
                        if not tasks and "title" in day_data:
                            tasks = [{"title": day_data["title"], "description": day_data.get("description", "")}]
                        for order, task in enumerate(tasks):
                            daily_task = DailyTask(
                                weekly_task_id=weekly_task.id,
                                day_number=day_data["day_number"],
                                order=order,
                                title=task["title"],
                                description=task.get("description", ""),
                            )
                            db.add(daily_task)

    db.commit()
    state["roadmap_id"] = str(roadmap.id)
    return state
