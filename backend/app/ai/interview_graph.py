"""LangGraph workflow for SMART-based interview."""
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

from langgraph.graph import StateGraph, END

from app.ai.interview_state import InterviewState
from app.ai.nodes.interview_nodes import question_generator, answer_analyzer


def create_question_graph():
    """Create LangGraph workflow for generating questions."""
    workflow = StateGraph(InterviewState)
    workflow.add_node("question_generator", question_generator)
    workflow.set_entry_point("question_generator")
    workflow.add_edge("question_generator", END)
    return workflow.compile()


def create_analysis_graph():
    """Create LangGraph workflow for analyzing answers."""
    workflow = StateGraph(InterviewState)
    workflow.add_node("answer_analyzer", answer_analyzer)
    workflow.set_entry_point("answer_analyzer")
    workflow.add_edge("answer_analyzer", END)
    return workflow.compile()


# Thread pool for running sync graph in async context
_executor = ThreadPoolExecutor(max_workers=4)


async def generate_questions(topic: str, duration_months: int) -> dict:
    """Generate SMART interview questions.

    Args:
        topic: Learning topic
        duration_months: Duration in months

    Returns:
        Dict with session_id, questions, and round
    """
    session_id = str(uuid.uuid4())

    initial_state: InterviewState = {
        "topic": topic,
        "duration_months": duration_months,
        "session_id": session_id,
        "questions": [],
        "answers": [],
        "round": 1,
        "needs_followup": False,
        "interview_context": None,
        "error_message": None,
    }

    graph = create_question_graph()

    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        _executor,
        graph.invoke,
        initial_state
    )

    return {
        "session_id": session_id,
        "questions": final_state["questions"],
        "round": final_state["round"],
        "error_message": final_state.get("error_message"),
    }


async def analyze_answers(
    topic: str,
    duration_months: int,
    session_id: str,
    questions: list,
    answers: list,
    current_round: int,
) -> dict:
    """Analyze interview answers and determine next steps.

    Args:
        topic: Learning topic
        duration_months: Duration in months
        session_id: Interview session ID
        questions: Current questions
        answers: All answers so far
        current_round: Current interview round

    Returns:
        Dict with status, followup_questions (if needed), and interview_context
    """
    initial_state: InterviewState = {
        "topic": topic,
        "duration_months": duration_months,
        "session_id": session_id,
        "questions": questions,
        "answers": answers,
        "round": current_round,
        "needs_followup": False,
        "interview_context": None,
        "error_message": None,
    }

    graph = create_analysis_graph()

    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        _executor,
        graph.invoke,
        initial_state
    )

    if final_state["needs_followup"]:
        return {
            "status": "followup_needed",
            "round": final_state["round"],
            "followup_questions": final_state["questions"],
            "interview_context": final_state["interview_context"],
        }
    else:
        return {
            "status": "completed",
            "round": final_state["round"],
            "followup_questions": None,
            "interview_context": final_state["interview_context"],
        }
