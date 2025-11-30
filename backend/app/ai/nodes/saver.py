from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Roadmap, MonthlyGoal, WeeklyTask, DailyTask
from app.ai.state import RoadmapGenerationState


def save_roadmap(state: RoadmapGenerationState, db: Session) -> RoadmapGenerationState:
    """Save the generated roadmap to the database."""
    # Calculate end date
    end_date = state["start_date"] + timedelta(days=state["duration_months"] * 30)

    # Create roadmap with schedule info
    roadmap = Roadmap(
        user_id=UUID(state["user_id"]),
        title=state["title"],
        description=state["description"],
        topic=state["topic"],
        duration_months=state["duration_months"],
        start_date=state["start_date"],
        end_date=end_date,
        mode=state["mode"],
        # Schedule fields
        daily_available_minutes=state.get("daily_available_minutes", 60),
        rest_days=state.get("rest_days", []),
        intensity=state.get("intensity", "moderate"),
    )
    db.add(roadmap)
    db.flush()  # Get the roadmap ID

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
        weekly_data = next(
            (w for w in state["weekly_tasks"] if w["month_number"] == monthly_data["month_number"]),
            None
        )
        if weekly_data:
            for weekly_task_data in weekly_data["weekly_tasks"]:
                weekly_task = WeeklyTask(
                    monthly_goal_id=monthly_goal.id,
                    week_number=weekly_task_data["week_number"],
                    title=weekly_task_data["title"],
                    description=weekly_task_data["description"],
                )
                db.add(weekly_task)
                db.flush()

                # Find daily tasks for this week
                daily_month_data = next(
                    (d for d in state["daily_tasks"] if d["month_number"] == monthly_data["month_number"]),
                    None
                )
                if daily_month_data:
                    daily_week_data = next(
                        (w for w in daily_month_data["weeks"] if w["week_number"] == weekly_task_data["week_number"]),
                        None
                    )
                    if daily_week_data:
                        for daily_task_data in daily_week_data["daily_tasks"]:
                            daily_task = DailyTask(
                                weekly_task_id=weekly_task.id,
                                day_number=daily_task_data["day_number"],
                                title=daily_task_data["title"],
                                description=daily_task_data["description"],
                            )
                            db.add(daily_task)

    db.commit()
    state["roadmap_id"] = str(roadmap.id)
    return state
