"""Simplified LangGraph workflow for roadmap generation.

Flow: goal_analyzer → monthly_generator → weekly_generator → daily_generator → saver
Total: 4 LLM calls (one per stage)
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.ai.state import RoadmapGenerationState
from app.ai.nodes.goal_analyzer import goal_analyzer
from app.ai.nodes.monthly_generator import monthly_generator
from app.ai.nodes.weekly_generator import weekly_generator
from app.ai.nodes.daily_generator import daily_generator
from app.ai.nodes.saver import save_roadmap


def create_roadmap_graph():
    """Create simplified LangGraph workflow."""
    workflow = StateGraph(RoadmapGenerationState)

    # Add nodes (4 LLM calls total)
    workflow.add_node("goal_analyzer", goal_analyzer)
    workflow.add_node("monthly_generator", monthly_generator)
    workflow.add_node("weekly_generator", weekly_generator)
    workflow.add_node("daily_generator", daily_generator)

    # Linear flow
    workflow.set_entry_point("goal_analyzer")
    workflow.add_edge("goal_analyzer", "monthly_generator")
    workflow.add_edge("monthly_generator", "weekly_generator")
    workflow.add_edge("weekly_generator", "daily_generator")
    workflow.add_edge("daily_generator", END)

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
) -> dict:
    """Generate a complete roadmap using LangGraph.

    Args:
        topic: Learning topic
        duration_months: Number of months (1-6)
        start_date: Start date
        mode: Roadmap mode (planning)
        user_id: User ID
        db: Database session

    Returns:
        Dict with roadmap_id, title, and status
    """
    # Initialize state
    initial_state: RoadmapGenerationState = {
        "topic": topic,
        "duration_months": duration_months,
        "start_date": start_date,
        "mode": mode,
        "user_id": user_id,
        "title": None,
        "description": None,
        "monthly_goals": [],
        "weekly_tasks": [],
        "daily_tasks": [],
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

    # Save to database
    final_state = save_roadmap(final_state, db)

    return {
        "roadmap_id": final_state["roadmap_id"],
        "title": final_state["title"],
        "error_message": final_state.get("error_message"),
    }
