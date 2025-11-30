"""단순화된 인터뷰 시스템 - 고정 질문 + AI 보완 1회

흐름:
1. 고정 SMART 질문 표시 (라운드 1)
2. 사용자 답변 수집
3. AI 추가 질문 생성 (라운드 2, 필요시)
4. 사용자 추가 답변
5. 컨텍스트 컴파일 후 완료
"""
import json
import uuid
import copy
from typing import Dict, List, Any, Optional

from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.prompts.interview_prompts import (
    FIXED_SMART_QUESTIONS,
    AI_FOLLOWUP_PROMPT,
    SIMPLE_COMPILE_CONTEXT_PROMPT,
    get_mode_description,
)


# ============ Constants ============
MAX_ROUNDS = 2  # 고정 질문 1회 + AI 추가질문 1회


class InterviewGenerationError(Exception):
    """Raised when AI fails to generate interview questions."""
    pass


# ============ Start Interview (고정 질문 반환) ============

def start_interview(
    topic: str,
    mode: str,
    duration_months: int,
    user_id: str,
    session_id: Optional[str] = None,
    callbacks: Optional[List[Any]] = None,
    search_context: str = "",
) -> Dict[str, Any]:
    """Start a new interview session with fixed SMART questions.

    단순화: AI 호출 없이 고정 질문만 반환
    """
    sid = session_id or str(uuid.uuid4())

    # 고정 질문 복사 (원본 수정 방지)
    questions = copy.deepcopy(FIXED_SMART_QUESTIONS)

    # Create state
    state = {
        "session_id": sid,
        "topic": topic,
        "mode": mode,
        "duration_months": duration_months,
        "user_id": user_id,
        "current_round": 1,
        "max_rounds": MAX_ROUNDS,
        "all_questions": questions,
        "current_questions": questions,
        "all_answers": [],
        "is_complete": False,
        "compiled_context": None,
        "key_insights": [],
        "extracted_daily_minutes": None,
        "extracted_rest_days": None,
        "extracted_intensity": None,
        "search_context": search_context,
    }

    return {
        "session_id": sid,
        "current_round": 1,
        "max_rounds": MAX_ROUNDS,
        "questions": questions,
        "is_complete": False,
        "state": state,
    }


# ============ Submit Answers ============

def submit_answers(
    state: Dict[str, Any],
    answers: List[Dict[str, str]],
    callbacks: Optional[List[Any]] = None,
    user_wants_complete: bool = False,
) -> Dict[str, Any]:
    """Submit answers for current round.

    단순화된 흐름:
    - 라운드 1: 고정 질문 답변 → AI 추가질문 생성
    - 라운드 2: 추가질문 답변 → 완료
    """
    current_round = state.get("current_round", 1)
    topic = state["topic"]
    mode = state["mode"]
    duration_months = state["duration_months"]

    print(f"\n[INTERVIEW] submit_answers() - Round {current_round}")
    print(f"[INTERVIEW] Received {len(answers)} answers")

    # 답변 저장
    answer_map = {a["question_id"]: a for a in state.get("all_answers", [])}
    for a in answers:
        answer_map[a["question_id"]] = a
    state["all_answers"] = list(answer_map.values())

    # 라운드 2이거나, 사용자가 완료 원하면 → 완료
    if current_round >= MAX_ROUNDS or user_wants_complete:
        return _complete_interview(state)

    # 라운드 1: AI 추가질문 생성
    followup_questions = _generate_ai_followup(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        questions=state["current_questions"],
        answers=state["all_answers"],
    )

    # 추가질문이 없으면 바로 완료
    if not followup_questions:
        print("[INTERVIEW] No followup questions needed, completing...")
        return _complete_interview(state)

    # 라운드 2로 진행
    print(f"[INTERVIEW] Generated {len(followup_questions)} followup questions")

    state["current_round"] = 2
    state["current_questions"] = followup_questions
    state["all_questions"] = state.get("all_questions", []) + followup_questions

    return {
        "session_id": state["session_id"],
        "current_round": 2,
        "max_rounds": MAX_ROUNDS,
        "questions": followup_questions,
        "is_complete": False,
        "is_followup": True,
        "state": state,
    }


# ============ AI Followup Question Generation ============

def _generate_ai_followup(
    topic: str,
    mode: str,
    duration_months: int,
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """AI가 추가질문 생성 (1회만)"""
    llm = create_llm(temperature=0.5)

    # 답변 텍스트 구성
    answer_map = {a["question_id"]: a["answer"] for a in answers}
    qa_lines = []
    for q in questions:
        answer = answer_map.get(q["id"], "(미응답)")
        qa_lines.append(f"Q: {q['question']}")
        qa_lines.append(f"A: {answer}")
        qa_lines.append("")

    user_answers = "\n".join(qa_lines)

    prompt = AI_FOLLOWUP_PROMPT.format(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        user_answers=user_answers,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)

        if not result.get("needs_followup", False):
            return []

        followup_questions = result.get("followup_questions", [])

        # ID 및 필수 필드 보장
        for i, q in enumerate(followup_questions):
            if "id" not in q:
                q["id"] = f"followup_{i}"
            if "question_type" not in q:
                q["question_type"] = "textarea"

        return followup_questions[:3]  # 최대 3개

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[INTERVIEW] AI followup generation failed: {e}")
        return []


# ============ Complete Interview ============

def _complete_interview(state: Dict[str, Any]) -> Dict[str, Any]:
    """인터뷰 완료 및 컨텍스트 컴파일"""

    # 컨텍스트 컴파일
    context_result = _compile_context(
        topic=state["topic"],
        mode=state["mode"],
        duration_months=state["duration_months"],
        questions=state.get("all_questions", []),
        answers=state.get("all_answers", []),
    )

    # State 업데이트
    state["is_complete"] = True
    state["compiled_context"] = context_result["compiled_context"]
    state["key_insights"] = context_result["key_insights"]
    state["extracted_daily_minutes"] = context_result["extracted_daily_minutes"]
    state["extracted_rest_days"] = context_result["extracted_rest_days"]
    state["extracted_intensity"] = context_result["extracted_intensity"]

    print(f"[INTERVIEW] Interview completed!")
    print(f"[INTERVIEW] Context: {context_result['compiled_context'][:100]}...")

    return {
        "session_id": state["session_id"],
        "current_round": state.get("current_round", 1),
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


def _compile_context(
    topic: str,
    mode: str,
    duration_months: int,
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """컨텍스트 컴파일"""
    llm = create_llm(temperature=0.3)

    # Q&A 텍스트 구성
    answer_map = {a["question_id"]: a["answer"] for a in answers}
    qa_lines = []
    for q in questions:
        answer = answer_map.get(q["id"], "")
        if answer:
            qa_lines.append(f"Q: {q['question']}")
            qa_lines.append(f"A: {answer}")
            qa_lines.append("")

    interview_qa = "\n".join(qa_lines)

    prompt = SIMPLE_COMPILE_CONTEXT_PROMPT.format(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        interview_qa=interview_qa,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)
        schedule = result.get("extracted_schedule", {})

        return {
            "compiled_context": result.get("compiled_context", ""),
            "key_insights": result.get("key_insights", []),
            "extracted_daily_minutes": schedule.get("daily_minutes", 60),
            "extracted_rest_days": schedule.get("rest_days", [5, 6]),
            "extracted_intensity": schedule.get("intensity", "moderate"),
        }

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[INTERVIEW] Context compilation failed: {e}")
        # Fallback
        return _extract_context_fallback(questions, answers)


def _extract_context_fallback(
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Fallback 컨텍스트 추출"""
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    context_parts = []
    key_insights = []
    for q in questions:
        answer = answer_map.get(q["id"], "")
        if answer:
            context_parts.append(f"- {q['question']}: {answer}")
            if len(key_insights) < 3 and len(answer) > 5:
                key_insights.append(answer[:100])

    return {
        "compiled_context": "\n".join(context_parts),
        "key_insights": key_insights,
        "extracted_daily_minutes": 60,
        "extracted_rest_days": [5, 6],
        "extracted_intensity": "moderate",
    }


# ============ Legacy Compatibility ============
# 기존 코드와 호환성을 위한 함수들

def generate_interview_questions(*args, **kwargs):
    """Legacy: 고정 질문 반환"""
    return {
        "questions": copy.deepcopy(FIXED_SMART_QUESTIONS),
        "smart_coverage": {
            "specific": True,
            "measurable": False,
            "achievable": True,
            "relevant": True,
            "time_bound": True,
        },
    }


def compile_interview_context(
    topic: str,
    mode: str,
    duration_months: int,
    all_questions: List[Dict[str, Any]],
    all_answers: List[Dict[str, str]],
    evaluations: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Legacy: 컨텍스트 컴파일"""
    return _compile_context(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        questions=all_questions,
        answers=all_answers,
    )
