"""Simplified LangGraph workflow for roadmap generation.

Flow: goal_analyzer → monthly_generator → weekly_generator → saver
Total: 3 LLM calls (one per stage)

Daily tasks are generated lazily (on-demand) when user completes previous week.
First week's daily tasks are generated automatically after roadmap creation.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.ai.state import RoadmapGenerationState
from app.ai.nodes.goal_analyzer import goal_analyzer
from app.ai.nodes.monthly_generator import monthly_generator
from app.ai.nodes.weekly_generator import weekly_generator
from app.ai.nodes.saver import save_roadmap


def create_roadmap_graph():
    """Create simplified LangGraph workflow.

    Note: daily_generator is removed from the main flow.
    First week's daily tasks are generated after saving via DailyGenerationService.
    """
    workflow = StateGraph(RoadmapGenerationState)

    # Add nodes (3 LLM calls total - daily tasks generated lazily)
    workflow.add_node("goal_analyzer", goal_analyzer)
    workflow.add_node("monthly_generator", monthly_generator)
    workflow.add_node("weekly_generator", weekly_generator)

    # Linear flow (no daily_generator - generated lazily per week)
    workflow.set_entry_point("goal_analyzer")
    workflow.add_edge("goal_analyzer", "monthly_generator")
    workflow.add_edge("monthly_generator", "weekly_generator")
    workflow.add_edge("weekly_generator", END)

    return workflow.compile()


# Thread pool for running sync graph in async context
_executor = ThreadPoolExecutor(max_workers=4)


async def generate_roadmap(
    topic: str,
    duration_months: int,
    start_date,
    mode,
    user_id: str,
    db: Session,
    interview_context: dict = None,
) -> dict:
    """Generate a complete roadmap using LangGraph.

    Args:
        topic: Learning topic
        duration_months: Number of months (1-6)
        start_date: Start date
        mode: Roadmap mode (planning)
        user_id: User ID
        db: Database session
        interview_context: SMART interview context (optional)

    Returns:
        Dict with roadmap_id, title, and status

    Note:
        Daily tasks are NOT generated in the main flow.
        First week's daily tasks are generated automatically after saving.
        Subsequent weeks are generated lazily when user completes previous week.
    """
    # Initialize state (no daily_tasks - generated lazily)
    initial_state: RoadmapGenerationState = {
        "topic": topic,
        "duration_months": duration_months,
        "start_date": start_date,
        "mode": mode,
        "user_id": user_id,
        "interview_context": interview_context,
        "title": None,
        "description": None,
        "monthly_goals": [],
        "weekly_tasks": [],
        "daily_tasks": [],  # Empty - first week generated after save
        "error_message": None,
        "roadmap_id": None,
    }

    # Create graph
    graph = create_roadmap_graph()

    # Run graph in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        _executor,
        graph.invoke,
        initial_state
    )

    # Save to database (without daily tasks)
    final_state = save_roadmap(final_state, db)

    # Generate first week's daily tasks
    try:
        await _generate_first_week_daily_tasks(
            final_state["roadmap_id"],
            user_id,
            db,
            interview_context,
        )
    except Exception as e:
        # Log but don't fail - first week can be generated manually
        final_state["error_message"] = f"첫 주 일일 태스크 생성 실패: {str(e)}"

    return {
        "roadmap_id": final_state["roadmap_id"],
        "title": final_state["title"],
        "error_message": final_state.get("error_message"),
    }


async def _generate_first_week_daily_tasks(
    roadmap_id: str,
    user_id: str,
    db: Session,
    interview_context: dict = None,
):
    """Generate daily tasks for the first week of the roadmap."""
    from uuid import UUID
    from app.models import MonthlyGoal, WeeklyTask
    from app.services.daily_generation_service import DailyGenerationService

    # Find first week (month 1, week 1)
    first_week = (
        db.query(WeeklyTask)
        .join(MonthlyGoal)
        .filter(
            MonthlyGoal.roadmap_id == UUID(roadmap_id),
            MonthlyGoal.month_number == 1,
            WeeklyTask.week_number == 1,
        )
        .first()
    )

    if first_week:
        service = DailyGenerationService(db)
        await service.generate_daily_tasks_for_week(
            first_week.id,
            UUID(user_id),
            force=True,  # First week always allowed
            interview_context=interview_context,
        )
