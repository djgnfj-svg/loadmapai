"""Context compiler node for deep interview system.

Compiles all interview data into a structured context for roadmap generation.
"""
import json
from typing import List, Dict, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import (
    DeepInterviewState,
    InterviewQuestionData,
    InterviewAnswerData,
)
from app.ai.prompts.interview_prompts import COMPILE_CONTEXT_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,
    )


def _format_full_interview_data(state: DeepInterviewState) -> str:
    """Format all interview data for context compilation."""
    sections = []
    stage_names = {
        1: "Stage 1: 목표 구체화 (Where to)",
        2: "Stage 2: 현재 상태 파악 (Where from)",
        3: "Stage 3: 제약 조건",
    }

    for stage_num in [1, 2, 3]:
        stage_data = state.get("stage_data", {}).get(stage_num)
        if not stage_data:
            continue

        section_parts = [f"\n=== {stage_names[stage_num]} ==="]

        # Main questions and answers
        questions = stage_data.get("questions", [])
        answers = stage_data.get("answers", [])
        questions_by_id = {q["id"]: q for q in questions}

        for answer in answers:
            question = questions_by_id.get(answer["question_id"])
            if question:
                section_parts.append(f"Q: {question['question']}")
                section_parts.append(f"A: {answer['answer']}")
                section_parts.append("")

        # Follow-up questions and answers
        followup_questions = stage_data.get("followup_questions", [])
        followup_answers = stage_data.get("followup_answers", [])
        if followup_questions:
            followup_by_id = {q["id"]: q for q in followup_questions}
            for answer in followup_answers:
                question = followup_by_id.get(answer["question_id"])
                if question:
                    section_parts.append(f"Q (후속): {question['question']}")
                    section_parts.append(f"A: {answer['answer']}")
                    section_parts.append("")

        sections.append("\n".join(section_parts))

    return "\n".join(sections)


def _parse_daily_time(time_str: str) -> int:
    """Parse daily time string to minutes."""
    time_mapping = {
        "30분 이하": 30,
        "30분~1시간": 45,
        "1~2시간": 90,
        "2~3시간": 150,
        "3시간 이상": 210,
    }
    for key, value in time_mapping.items():
        if key in time_str:
            return value
    return 60  # Default


def _parse_rest_days(rest_str: str) -> List[int]:
    """Parse rest days string to list of day numbers (0=Sunday, 6=Saturday)."""
    if "쉬는 날 없음" in rest_str or "매일" in rest_str:
        return []
    elif "주말만" in rest_str or "토,일" in rest_str:
        return [0, 6]  # Sunday and Saturday
    elif "일요일만" in rest_str:
        return [0]
    elif "토요일만" in rest_str:
        return [6]
    return []


def _parse_intensity(intensity_str: str) -> str:
    """Parse intensity string to standard value."""
    if "여유" in intensity_str or "천천히" in intensity_str:
        return "light"
    elif "빡세게" in intensity_str or "도전" in intensity_str:
        return "intense"
    return "moderate"


def _extract_schedule_from_stage3(state: DeepInterviewState) -> Dict:
    """Extract schedule information from Stage 3 answers."""
    stage3_data = state.get("stage_data", {}).get(3, {})
    answers = stage3_data.get("answers", [])

    daily_minutes = None
    rest_days = None
    intensity = None

    for answer in answers:
        qid = answer.get("question_id", "")
        ans = answer.get("answer", "")

        if "daily_time" in qid or "시간" in ans:
            if any(t in ans for t in ["30분", "1시간", "2시간", "3시간"]):
                daily_minutes = _parse_daily_time(ans)

        if "rest_days" in qid or "쉬는" in qid:
            rest_days = _parse_rest_days(ans)

        if "intensity" in qid or "강도" in qid:
            intensity = _parse_intensity(ans)

    return {
        "daily_minutes": daily_minutes or 60,
        "rest_days": rest_days or [],
        "intensity": intensity or "moderate",
    }


def compile_interview_context(state: DeepInterviewState) -> DeepInterviewState:
    """Compile all interview data into a structured context.

    This node:
    1. Gathers all Q&A from all 3 stages
    2. Uses AI to extract key insights
    3. Compiles a formatted context for roadmap generation
    4. Extracts schedule constraints from Stage 3
    """
    llm = create_llm()

    full_interview_data = _format_full_interview_data(state)

    prompt = COMPILE_CONTEXT_PROMPT.format(
        topic=state["topic"],
        mode=state["mode"],
        duration_months=state["duration_months"],
        full_interview_data=full_interview_data,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)

        state["compiled_context"] = result.get("compiled_context", "")
        state["key_insights"] = result.get("key_insights", [])

        # Extract schedule info
        extracted_schedule = result.get("extracted_schedule", {})
        state["extracted_daily_minutes"] = extracted_schedule.get("daily_minutes")
        state["extracted_rest_days"] = extracted_schedule.get("rest_days")
        state["extracted_intensity"] = extracted_schedule.get("intensity")

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: use raw interview data as context
        state["compiled_context"] = full_interview_data
        state["key_insights"] = []

        # Try to extract schedule from Stage 3 directly
        schedule = _extract_schedule_from_stage3(state)
        state["extracted_daily_minutes"] = schedule["daily_minutes"]
        state["extracted_rest_days"] = schedule["rest_days"]
        state["extracted_intensity"] = schedule["intensity"]

    # Mark interview as complete
    state["is_complete"] = True

    return state
