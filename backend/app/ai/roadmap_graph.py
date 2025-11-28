from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.ai.state import RoadmapGenerationState
from app.ai.nodes.goal_analyzer import goal_analyzer
from app.ai.nodes.monthly_generator import monthly_generator
from app.ai.nodes.weekly_generator import weekly_generator
from app.ai.nodes.daily_generator import daily_generator
from app.ai.nodes.validator import validator, should_retry
from app.ai.nodes.saver import save_roadmap
from app.ai.nodes.interview_generator import (
    format_interview_context,
    extract_daily_time,
    extract_schedule_from_answers,
)


def create_roadmap_graph():
    """Create the LangGraph workflow for roadmap generation."""
    workflow = StateGraph(RoadmapGenerationState)

    # Add nodes
    workflow.add_node("goal_analyzer", goal_analyzer)
    workflow.add_node("monthly_generator", monthly_generator)
    workflow.add_node("weekly_generator", weekly_generator)
    workflow.add_node("daily_generator", daily_generator)
    workflow.add_node("validator", validator)

    # Set entry point
    workflow.set_entry_point("goal_analyzer")

    # Add edges
    workflow.add_edge("goal_analyzer", "monthly_generator")
    workflow.add_edge("monthly_generator", "weekly_generator")
    workflow.add_edge("weekly_generator", "daily_generator")
    workflow.add_edge("daily_generator", "validator")

    # Add conditional edge for retry logic
    workflow.add_conditional_edges(
        "validator",
        should_retry,
        {
            "save": END,
            "retry": "monthly_generator",  # Retry from monthly generation
        }
    )

    return workflow.compile()


async def generate_roadmap(
    topic: str,
    duration_months: int,
    start_date,
    mode,
    user_id: str,
    db: Session,
) -> dict:
    """Generate a complete roadmap using LangGraph."""
    # Initialize state
    initial_state: RoadmapGenerationState = {
        "topic": topic,
        "duration_months": duration_months,
        "start_date": start_date,
        "mode": mode,
        "user_id": user_id,
        "interview_context": None,
        "daily_time": None,
        "title": None,
        "description": None,
        "monthly_goals": [],
        "weekly_tasks": [],
        "daily_tasks": [],
        "current_month": 1,
        "current_week": 1,
        "validation_passed": False,
        "error_message": None,
        "retry_count": 0,
        "roadmap_id": None,
    }

    # Create and run the graph
    graph = create_roadmap_graph()
    final_state = graph.invoke(initial_state)

    # Save to database
    final_state = save_roadmap(final_state, db)

    return {
        "roadmap_id": final_state["roadmap_id"],
        "title": final_state["title"],
        "validation_passed": final_state["validation_passed"],
        "error_message": final_state.get("error_message"),
    }


async def generate_roadmap_with_context(
    topic: str,
    duration_months: int,
    start_date,
    mode,
    user_id: str,
    interview_answers: List[Dict[str, str]],
    interview_questions: List[Dict[str, Any]],
    db: Session,
) -> dict:
    """Generate a complete roadmap using LangGraph with interview context."""
    # Format interview context
    interview_context = format_interview_context(interview_answers, interview_questions)
    daily_time = extract_daily_time(interview_answers)

    # Extract schedule info from interview answers
    schedule_info = extract_schedule_from_answers(interview_answers)

    # Initialize state with interview context and schedule
    initial_state: RoadmapGenerationState = {
        "topic": topic,
        "duration_months": duration_months,
        "start_date": start_date,
        "mode": mode,
        "user_id": user_id,
        "interview_context": interview_context,
        "daily_time": daily_time,
        # Schedule info
        "daily_available_minutes": schedule_info["daily_available_minutes"],
        "rest_days": schedule_info["rest_days"],
        "intensity": schedule_info["intensity"],
        # Generation state
        "title": None,
        "description": None,
        "monthly_goals": [],
        "weekly_tasks": [],
        "daily_tasks": [],
        "current_month": 1,
        "current_week": 1,
        "validation_passed": False,
        "error_message": None,
        "retry_count": 0,
        "roadmap_id": None,
    }

    # Create and run the graph
    graph = create_roadmap_graph()
    final_state = graph.invoke(initial_state)

    # Save to database with schedule info
    final_state = save_roadmap(final_state, db)

    return {
        "roadmap_id": final_state["roadmap_id"],
        "title": final_state["title"],
        "validation_passed": final_state["validation_passed"],
        "error_message": final_state.get("error_message"),
    }
