"""LangGraph workflow for multi-stage deep interview system.

The interview consists of 3 stages:
1. Goal Clarification (Where to) - What do you want to achieve? Why?
2. Current State (Where from) - What do you already know? Experience?
3. Constraints - Time, deadlines, resources

Each stage:
- AI generates questions based on topic, mode, and previous answers
- User answers are evaluated for quality
- Follow-up questions are generated if answers are vague
- Once sufficient info is gathered, advances to next stage
"""
import uuid
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END

from app.ai.state import (
    DeepInterviewState,
    InterviewQuestionData,
    InterviewAnswerData,
    StageData,
)
from app.ai.nodes.stage_question_generator import (
    generate_stage_questions,
    generate_followup_questions,
    advance_to_next_stage,
)
from app.ai.nodes.answer_evaluator import (
    evaluate_answers,
    should_probe_deeper,
)
from app.ai.nodes.context_compiler import compile_interview_context


def create_interview_graph():
    """Create the LangGraph workflow for deep interview.

    The workflow handles question generation and answer evaluation.
    User answers are provided externally via API between graph invocations.

    Flow:
    generate_questions -> [wait for user answers] -> evaluate_answers
        -> should_probe_deeper:
            - "probe" -> generate_followup_questions -> [wait]
            - "next_stage" -> advance_to_next_stage -> generate_questions (if < 3)
            - "complete" -> compile_context -> END
    """
    workflow = StateGraph(DeepInterviewState)

    # Add nodes
    workflow.add_node("generate_questions", generate_stage_questions)
    workflow.add_node("evaluate_answers", evaluate_answers)
    workflow.add_node("generate_followups", generate_followup_questions)
    workflow.add_node("advance_stage", advance_to_next_stage)
    workflow.add_node("compile_context", compile_interview_context)

    # Set entry point - we'll control flow manually based on state
    workflow.set_entry_point("generate_questions")

    # Add edges
    workflow.add_edge("generate_questions", END)  # Pause for user input
    workflow.add_edge("generate_followups", END)  # Pause for user input

    # After evaluation, decide what to do next
    workflow.add_conditional_edges(
        "evaluate_answers",
        should_probe_deeper,
        {
            "probe": "generate_followups",
            "next_stage": "advance_stage",
            "complete": "compile_context",
        }
    )

    # After advancing stage, generate new questions
    workflow.add_edge("advance_stage", "generate_questions")

    # After compiling context, we're done
    workflow.add_edge("compile_context", END)

    return workflow.compile()


def create_evaluation_graph():
    """Create a graph specifically for evaluating answers.

    This is invoked after user provides answers.
    """
    workflow = StateGraph(DeepInterviewState)

    workflow.add_node("evaluate_answers", evaluate_answers)
    workflow.add_node("generate_followups", generate_followup_questions)
    workflow.add_node("advance_stage", advance_to_next_stage)
    workflow.add_node("generate_questions", generate_stage_questions)
    workflow.add_node("compile_context", compile_interview_context)

    workflow.set_entry_point("evaluate_answers")

    workflow.add_conditional_edges(
        "evaluate_answers",
        should_probe_deeper,
        {
            "probe": "generate_followups",
            "next_stage": "advance_stage",
            "complete": "compile_context",
        }
    )

    workflow.add_edge("generate_followups", END)
    workflow.add_edge("advance_stage", "generate_questions")
    workflow.add_edge("generate_questions", END)
    workflow.add_edge("compile_context", END)

    return workflow.compile()


def create_initial_state(
    topic: str,
    mode: str,
    duration_months: int,
    user_id: str,
    session_id: Optional[str] = None,
    max_followups_per_stage: int = 2,
) -> DeepInterviewState:
    """Create initial state for a new interview session."""
    return DeepInterviewState(
        session_id=session_id or str(uuid.uuid4()),
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        user_id=user_id,
        current_stage=1,
        stages_completed=[],
        max_followups_per_stage=max_followups_per_stage,
        stage_data={},
        current_questions=[],
        current_answers=[],
        current_evaluations=[],
        followup_count=0,
        pending_followup_questions=[],
        is_complete=False,
        compiled_context=None,
        key_insights=[],
        extracted_daily_minutes=None,
        extracted_rest_days=None,
        extracted_intensity=None,
        error_message=None,
    )


def start_interview(
    topic: str,
    mode: str,
    duration_months: int,
    user_id: str,
    session_id: Optional[str] = None,
    callbacks: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Start a new interview session and generate Stage 1 questions.

    Args:
        topic: Learning topic
        mode: Learning mode (planning/learning)
        duration_months: Duration in months
        user_id: User ID
        session_id: Optional session ID
        callbacks: Optional list of LangChain callback handlers for streaming

    Returns:
        dict with session_id, current_stage, questions, and state
    """
    state = create_initial_state(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        user_id=user_id,
        session_id=session_id,
    )

    # Run the graph to generate initial questions
    graph = create_interview_graph()
    config = {"callbacks": callbacks} if callbacks else {}
    final_state = graph.invoke(state, config=config)

    return {
        "session_id": final_state["session_id"],
        "current_stage": final_state["current_stage"],
        "questions": final_state["current_questions"],
        "is_complete": final_state["is_complete"],
        "state": final_state,
    }


def submit_answers(
    state: DeepInterviewState,
    answers: List[InterviewAnswerData],
    callbacks: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Submit answers and get the next set of questions or completion.

    Args:
        state: Current interview state
        answers: User's answers to current questions
        callbacks: Optional list of LangChain callback handlers for streaming

    Returns:
        dict with updated state, questions (if any), and completion status
    """
    # Update state with answers
    state["current_answers"] = answers

    # Run evaluation graph
    graph = create_evaluation_graph()
    config = {"callbacks": callbacks} if callbacks else {}
    final_state = graph.invoke(state, config=config)

    result = {
        "session_id": final_state["session_id"],
        "current_stage": final_state["current_stage"],
        "questions": final_state["current_questions"],
        "is_complete": final_state["is_complete"],
        "state": final_state,
    }

    if final_state["is_complete"]:
        result["compiled_context"] = final_state["compiled_context"]
        result["key_insights"] = final_state["key_insights"]
        result["schedule"] = {
            "daily_minutes": final_state["extracted_daily_minutes"],
            "rest_days": final_state["extracted_rest_days"],
            "intensity": final_state["extracted_intensity"],
        }

    return result


def get_interview_summary(state: DeepInterviewState) -> Dict[str, Any]:
    """Get a summary of the current interview state.

    Returns:
        dict with stage info, completion status, and insights
    """
    stages_info = []
    for stage_num in [1, 2, 3]:
        stage_data = state.get("stage_data", {}).get(stage_num)
        if stage_data:
            stages_info.append({
                "stage": stage_num,
                "questions_count": len(stage_data.get("questions", [])),
                "answers_count": len(stage_data.get("answers", [])),
                "completed": stage_num in state.get("stages_completed", []),
            })

    return {
        "session_id": state["session_id"],
        "topic": state["topic"],
        "mode": state["mode"],
        "current_stage": state["current_stage"],
        "stages": stages_info,
        "is_complete": state["is_complete"],
        "key_insights": state.get("key_insights", []),
    }


def serialize_state(state: DeepInterviewState) -> Dict[str, Any]:
    """Serialize state to JSON-compatible dict for storage."""
    # Convert TypedDicts to regular dicts
    serialized = dict(state)

    # Convert nested TypedDicts
    if serialized.get("stage_data"):
        serialized["stage_data"] = {
            k: dict(v) for k, v in serialized["stage_data"].items()
        }

    if serialized.get("current_questions"):
        serialized["current_questions"] = [
            dict(q) for q in serialized["current_questions"]
        ]

    if serialized.get("current_answers"):
        serialized["current_answers"] = [
            dict(a) for a in serialized["current_answers"]
        ]

    if serialized.get("current_evaluations"):
        serialized["current_evaluations"] = [
            dict(e) for e in serialized["current_evaluations"]
        ]

    if serialized.get("pending_followup_questions"):
        serialized["pending_followup_questions"] = [
            dict(q) for q in serialized["pending_followup_questions"]
        ]

    return serialized


def deserialize_state(data: Dict[str, Any]) -> DeepInterviewState:
    """Deserialize state from JSON-compatible dict."""
    # This creates a DeepInterviewState from the dict
    # TypedDict works like a dict, so we can construct directly
    return DeepInterviewState(**data)
