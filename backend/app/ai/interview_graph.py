"""Simplified AI-driven interview system for roadmap generation.

Single-stage interview where AI generates all questions at once.
User answers, then context is compiled for roadmap generation.
"""
import json
import uuid
from typing import Dict, List, Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import DeepInterviewState
from app.ai.prompts.interview_prompts import (
    COMPREHENSIVE_INTERVIEW_PROMPT,
    COMPILE_CONTEXT_PROMPT,
    get_mode_description,
)


def create_llm():
    """Create LLM instance."""
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


def generate_interview_questions(
    topic: str,
    mode: str,
    duration_months: int,
) -> List[Dict[str, Any]]:
    """Generate all interview questions in one batch using AI.

    Returns a list of question dictionaries with:
    - id: unique question identifier
    - question: the question text
    - question_type: "single_choice" or "text"
    - options: list of options (for single_choice)
    - required_field: optional field name for required info
    """
    llm = create_llm()

    prompt = COMPREHENSIVE_INTERVIEW_PROMPT.format(
        topic=topic,
        mode=mode,
        mode_description=get_mode_description(mode),
        duration_months=duration_months,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        questions = result.get("questions", [])

        # Ensure all questions have required fields
        for i, q in enumerate(questions):
            if "id" not in q:
                q["id"] = f"q_{i}"
            if "question_type" not in q:
                q["question_type"] = "text"

        return questions

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback questions if AI generation fails
        return get_fallback_questions(topic)


def get_fallback_questions(topic: str) -> List[Dict[str, Any]]:
    """Return fallback questions if AI generation fails."""
    return [
        {
            "id": "current_level",
            "question": f"{topic} 관련 현재 실력은 어느 정도인가요?",
            "question_type": "single_choice",
            "options": ["처음 시작", "기초는 알아요", "어느 정도 해봤어요", "꽤 잘해요"],
            "required_field": "current_level"
        },
        {
            "id": "specific_goal",
            "question": f"{topic}을(를) 통해 무엇을 이루고 싶으신가요?",
            "question_type": "text",
            "placeholder": "구체적인 목표를 알려주세요",
            "required_field": "specific_goal"
        },
        {
            "id": "daily_time",
            "question": "하루에 얼마나 시간을 투자할 수 있나요?",
            "question_type": "single_choice",
            "options": ["30분 이하", "30분~1시간", "1~2시간", "2~3시간", "3시간 이상"],
            "required_field": "daily_time"
        },
        {
            "id": "rest_days",
            "question": "일주일 중 쉬는 날은 언제인가요?",
            "question_type": "single_choice",
            "options": ["쉬는 날 없이 매일", "주말(토,일) 휴식", "일요일만 휴식", "토요일만 휴식"],
            "required_field": "rest_days"
        },
        {
            "id": "intensity",
            "question": "원하는 학습 강도는요?",
            "question_type": "single_choice",
            "options": ["천천히 꼼꼼하게", "적당한 속도로", "빠르고 도전적으로"],
            "required_field": "intensity"
        },
    ]


def compile_interview_context(
    topic: str,
    mode: str,
    duration_months: int,
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Compile interview Q&A into context for roadmap generation.

    Returns:
        - compiled_context: text summary for roadmap generation
        - key_insights: list of key insights
        - extracted_schedule: daily_minutes, rest_days, intensity
        - roadmap_requirements: current_level, specific_goal, etc.
    """
    llm = create_llm()

    # Format Q&A for the prompt
    qa_lines = []
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    for q in questions:
        answer = answer_map.get(q["id"], "")
        qa_lines.append(f"Q: {q['question']}")
        qa_lines.append(f"A: {answer}")
        qa_lines.append("")

    interview_qa = "\n".join(qa_lines)

    prompt = COMPILE_CONTEXT_PROMPT.format(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        interview_qa=interview_qa,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)

        # Extract schedule with defaults
        schedule = result.get("extracted_schedule", {})

        return {
            "compiled_context": result.get("compiled_context", ""),
            "key_insights": result.get("key_insights", []),
            "extracted_daily_minutes": schedule.get("daily_minutes", 60),
            "extracted_rest_days": schedule.get("rest_days", [5, 6]),  # Sat, Sun
            "extracted_intensity": schedule.get("intensity", "moderate"),
            "roadmap_requirements": result.get("roadmap_requirements", {}),
        }

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback context extraction
        return extract_context_from_answers(questions, answers)


def extract_context_from_answers(
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Fallback context extraction from answers."""
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    # Extract daily minutes from answer
    daily_time = answer_map.get("daily_time", "1~2시간")
    if "30분 이하" in daily_time:
        daily_minutes = 30
    elif "30분~1시간" in daily_time:
        daily_minutes = 45
    elif "1~2시간" in daily_time:
        daily_minutes = 90
    elif "2~3시간" in daily_time:
        daily_minutes = 150
    else:
        daily_minutes = 180

    # Extract rest days
    rest_days_answer = answer_map.get("rest_days", "주말(토,일) 휴식")
    if "매일" in rest_days_answer:
        rest_days = []
    elif "주말" in rest_days_answer or "토,일" in rest_days_answer:
        rest_days = [5, 6]
    elif "일요일" in rest_days_answer:
        rest_days = [6]
    elif "토요일" in rest_days_answer:
        rest_days = [5]
    else:
        rest_days = [6]

    # Extract intensity
    intensity_answer = answer_map.get("intensity", "적당한 속도로")
    if "천천히" in intensity_answer or "꼼꼼" in intensity_answer:
        intensity = "light"
    elif "빠르" in intensity_answer or "도전" in intensity_answer:
        intensity = "intense"
    else:
        intensity = "moderate"

    # Build context
    context_parts = []
    for q in questions:
        answer = answer_map.get(q["id"], "")
        if answer:
            context_parts.append(f"- {q['question']}: {answer}")

    return {
        "compiled_context": "\n".join(context_parts),
        "key_insights": [answer_map.get("specific_goal", "")],
        "extracted_daily_minutes": daily_minutes,
        "extracted_rest_days": rest_days,
        "extracted_intensity": intensity,
        "roadmap_requirements": {
            "current_level": answer_map.get("current_level", "beginner"),
            "specific_goal": answer_map.get("specific_goal", ""),
        },
    }


# ============ API Interface Functions ============

def start_interview(
    topic: str,
    mode: str,
    duration_months: int,
    user_id: str,
    session_id: Optional[str] = None,
    callbacks: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Start a new interview session and generate all questions.

    This is a simplified single-stage interview.
    """
    sid = session_id or str(uuid.uuid4())

    # Generate all questions at once
    questions = generate_interview_questions(topic, mode, duration_months)

    # Create state
    state = {
        "session_id": sid,
        "topic": topic,
        "mode": mode,
        "duration_months": duration_months,
        "user_id": user_id,
        "current_stage": 1,
        "stages_completed": [],
        "stage_data": {},
        "current_questions": questions,
        "current_answers": [],
        "current_evaluations": [],
        "followup_count": 0,
        "pending_followup_questions": [],
        "is_complete": False,
        "compiled_context": None,
        "key_insights": [],
        "extracted_daily_minutes": None,
        "extracted_rest_days": None,
        "extracted_intensity": None,
        "error_message": None,
    }

    return {
        "session_id": sid,
        "current_stage": 1,
        "questions": questions,
        "is_complete": False,
        "state": state,
    }


def submit_answers(
    state: Dict[str, Any],
    answers: List[Dict[str, str]],
    callbacks: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Submit all answers and complete the interview.

    Since this is a single-stage interview, submitting answers completes it.
    """
    # Store answers
    state["current_answers"] = answers

    # Compile context
    context_result = compile_interview_context(
        topic=state["topic"],
        mode=state["mode"],
        duration_months=state["duration_months"],
        questions=state["current_questions"],
        answers=answers,
    )

    # Update state with compiled results
    state["is_complete"] = True
    state["compiled_context"] = context_result["compiled_context"]
    state["key_insights"] = context_result["key_insights"]
    state["extracted_daily_minutes"] = context_result["extracted_daily_minutes"]
    state["extracted_rest_days"] = context_result["extracted_rest_days"]
    state["extracted_intensity"] = context_result["extracted_intensity"]

    # Save to stage_data for compatibility
    state["stage_data"] = {
        1: {
            "questions": state["current_questions"],
            "answers": answers,
        }
    }
    state["stages_completed"] = [1]

    return {
        "session_id": state["session_id"],
        "current_stage": 1,
        "questions": [],
        "is_complete": True,
        "compiled_context": context_result["compiled_context"],
        "key_insights": context_result["key_insights"],
        "schedule": {
            "daily_minutes": context_result["extracted_daily_minutes"],
            "rest_days": context_result["extracted_rest_days"],
            "intensity": context_result["extracted_intensity"],
        },
        "state": state,
    }
