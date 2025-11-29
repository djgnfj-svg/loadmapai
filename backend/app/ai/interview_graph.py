"""AI-driven multi-round interview system for roadmap generation.

Multi-round interview flow:
1. AI generates all questions at once
2. User answers
3. AI evaluates answers (sufficient/ambiguous/invalid)
4. If ambiguous/invalid answers exist, generate follow-up questions
5. Repeat until all answers are sufficient or max rounds reached
6. Compile context for roadmap generation
"""
import json
import uuid
from typing import Dict, List, Any, Optional

from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.prompts.interview_prompts import (
    COMPREHENSIVE_INTERVIEW_PROMPT,
    COMPILE_CONTEXT_PROMPT,
    BATCH_ANSWER_EVALUATION_PROMPT,
    FOLLOWUP_QUESTIONS_PROMPT,
    TERMINATION_CHECK_PROMPT,
    get_mode_description,
)


# ============ Constants ============
MAX_ROUNDS = 3
MAX_CONSECUTIVE_INVALID = 3


# ============ Question Generation ============

class InterviewGenerationError(Exception):
    """Raised when AI fails to generate interview questions."""
    pass


def generate_interview_questions(
    topic: str,
    mode: str,
    duration_months: int,
) -> List[Dict[str, Any]]:
    """Generate all interview questions in one batch using AI.

    Raises:
        InterviewGenerationError: If AI fails to generate questions.
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
        result = parse_json_response(response.content)
        questions = result.get("questions", [])

        if not questions:
            raise InterviewGenerationError("AI가 질문을 생성하지 못했습니다.")

        # Ensure all questions have required fields
        for i, q in enumerate(questions):
            if "id" not in q:
                q["id"] = f"q_{i}"
            if "question_type" not in q:
                q["question_type"] = "text"

        return questions

    except json.JSONDecodeError as e:
        raise InterviewGenerationError(f"AI 응답 파싱 실패: {str(e)}")
    except KeyError as e:
        raise InterviewGenerationError(f"AI 응답 형식 오류: {str(e)}")


# ============ Answer Evaluation ============

def evaluate_answers(
    topic: str,
    mode: str,
    duration_months: int,
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Evaluate all answers and categorize them."""
    llm = create_llm(temperature=0.3)  # Lower temp for consistent evaluation

    # Build Q&A text
    answer_map = {a["question_id"]: a["answer"] for a in answers}
    qa_lines = []
    for q in questions:
        answer = answer_map.get(q["id"], "(미응답)")
        q_type = "객관식" if q.get("question_type") == "single_choice" else "주관식"
        options_str = f" [선택지: {', '.join(q.get('options', []))}]" if q.get("options") else ""
        qa_lines.append(f"[{q['id']}] ({q_type}{options_str})")
        qa_lines.append(f"Q: {q['question']}")
        qa_lines.append(f"A: {answer}")
        qa_lines.append("")

    questions_and_answers = "\n".join(qa_lines)

    prompt = BATCH_ANSWER_EVALUATION_PROMPT.format(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        questions_and_answers=questions_and_answers,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)
        return result
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: assume all sufficient
        return {
            "evaluations": [
                {"question_id": q["id"], "status": "sufficient", "extracted_value": answer_map.get(q["id"], "")}
                for q in questions
            ],
            "overall_quality": "good",
            "invalid_count": 0,
            "ambiguous_ids": [],
            "invalid_ids": [],
        }


def generate_followup_questions(
    topic: str,
    mode: str,
    current_round: int,
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
    evaluation: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate follow-up questions for ambiguous/invalid answers."""
    llm = create_llm()

    answer_map = {a["question_id"]: a["answer"] for a in answers}
    question_map = {q["id"]: q for q in questions}

    # Build items needing followup
    items = []
    for eval_item in evaluation.get("evaluations", []):
        if eval_item["status"] in ("ambiguous", "invalid"):
            q_id = eval_item["question_id"]
            q = question_map.get(q_id, {})
            items.append({
                "question_id": q_id,
                "original_question": q.get("question", ""),
                "original_answer": answer_map.get(q_id, ""),
                "status": eval_item["status"],
                "issue": eval_item.get("issue", ""),
                "issue_type": eval_item.get("issue_type", ""),
            })

    if not items:
        return {"followup_questions": [], "warning_message": None}

    items_text = json.dumps(items, ensure_ascii=False, indent=2)

    prompt = FOLLOWUP_QUESTIONS_PROMPT.format(
        topic=topic,
        mode=mode,
        current_round=current_round,
        items_needing_followup=items_text,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)
        return result
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: simple retry questions
        fallback_questions = []
        for item in items:
            fallback_questions.append({
                "id": f"{item['question_id']}_followup",
                "original_question_id": item["question_id"],
                "question": f"다시 답변해 주세요: {item['original_question']}",
                "question_type": "text",
                "is_retry": True,
            })
        return {"followup_questions": fallback_questions, "warning_message": None}


def check_termination(
    topic: str,
    total_rounds: int,
    invalid_count: int,
    consecutive_invalid: int,
    invalid_history: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Check if interview should be force terminated."""
    # Quick check without AI for obvious cases
    if consecutive_invalid >= MAX_CONSECUTIVE_INVALID:
        return {
            "should_terminate": True,
            "reason": f"연속 {consecutive_invalid}회 이상한 답변",
            "final_warning": None,
            "can_continue_with_defaults": True,
        }

    if invalid_count > 0 and len(invalid_history) > 0:
        hostile_count = sum(1 for h in invalid_history if h.get("issue_type") == "hostile")
        if hostile_count >= 2:
            return {
                "should_terminate": True,
                "reason": "적대적 답변 반복",
                "final_warning": None,
                "can_continue_with_defaults": False,
            }

    # For borderline cases, use AI
    if invalid_count >= 3 or consecutive_invalid >= 2:
        llm = create_llm(temperature=0.2)
        history_text = json.dumps(invalid_history, ensure_ascii=False, indent=2) if invalid_history else "없음"

        prompt = TERMINATION_CHECK_PROMPT.format(
            topic=topic,
            total_rounds=total_rounds,
            invalid_count=invalid_count,
            consecutive_invalid=consecutive_invalid,
            invalid_history=history_text,
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return parse_json_response(response.content)
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "should_terminate": False,
        "reason": None,
        "final_warning": None,
        "can_continue_with_defaults": True,
    }


# ============ Context Compilation ============

def compile_interview_context(
    topic: str,
    mode: str,
    duration_months: int,
    all_questions: List[Dict[str, Any]],
    all_answers: List[Dict[str, str]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compile interview Q&A into context for roadmap generation."""
    llm = create_llm()

    # Build Q&A with extracted values
    answer_map = {a["question_id"]: a["answer"] for a in all_answers}
    eval_map = {e["question_id"]: e for e in evaluations}

    qa_lines = []
    for q in all_questions:
        q_id = q["id"].replace("_followup", "")  # Use original ID
        answer = answer_map.get(q["id"], answer_map.get(q_id, ""))
        eval_item = eval_map.get(q["id"], eval_map.get(q_id, {}))
        extracted = eval_item.get("extracted_value", answer)

        qa_lines.append(f"Q: {q['question']}")
        qa_lines.append(f"A: {extracted if extracted else answer}")
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
        result = parse_json_response(response.content)
        schedule = result.get("extracted_schedule", {})

        return {
            "compiled_context": result.get("compiled_context", ""),
            "key_insights": result.get("key_insights", []),
            "extracted_daily_minutes": schedule.get("daily_minutes", 60),
            "extracted_rest_days": schedule.get("rest_days", [5, 6]),
            "extracted_intensity": schedule.get("intensity", "moderate"),
            "roadmap_requirements": result.get("roadmap_requirements", {}),
        }

    except (json.JSONDecodeError, KeyError) as e:
        return extract_context_from_answers(all_questions, all_answers)


def extract_context_from_answers(
    questions: List[Dict[str, Any]],
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Fallback context extraction from answers."""
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    # Build context from all Q&A
    context_parts = []
    key_insights = []
    for q in questions:
        q_id = q["id"].replace("_followup", "")
        answer = answer_map.get(q["id"], answer_map.get(q_id, ""))
        if answer:
            context_parts.append(f"- {q['question']}: {answer}")
            # First meaningful answer becomes a key insight
            if len(key_insights) < 3 and len(answer) > 5:
                key_insights.append(answer[:100])

    # Default schedule (will be refined by AI during context compilation)
    return {
        "compiled_context": "\n".join(context_parts),
        "key_insights": key_insights,
        "extracted_daily_minutes": 60,  # Default 1 hour
        "extracted_rest_days": [5, 6],  # Default weekends
        "extracted_intensity": "moderate",
        "roadmap_requirements": {
            "primary_goal": answer_map.get("main_goal", ""),
            "current_situation": answer_map.get("current_situation", ""),
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
    """Start a new interview session and generate all questions."""
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
        "current_round": 1,
        "max_rounds": MAX_ROUNDS,
        "all_questions": questions,  # Original questions
        "current_questions": questions,  # Questions for current round
        "all_answers": [],  # All collected answers
        "current_answers": [],
        "evaluations": [],  # All evaluations
        "invalid_history": [],  # History of invalid answers
        "invalid_count": 0,
        "consecutive_invalid": 0,
        "is_complete": False,
        "is_terminated": False,
        "termination_reason": None,
        "warning_message": None,
        "compiled_context": None,
        "key_insights": [],
        "extracted_daily_minutes": None,
        "extracted_rest_days": None,
        "extracted_intensity": None,
        "error_message": None,
        # Legacy fields for compatibility
        "current_stage": 1,
        "stages_completed": [],
        "stage_data": {},
        "followup_count": 0,
        "pending_followup_questions": [],
    }

    return {
        "session_id": sid,
        "current_round": 1,
        "max_rounds": MAX_ROUNDS,
        "questions": questions,
        "is_complete": False,
        "is_followup": False,
        "warning_message": None,
        "state": state,
    }


def submit_answers(
    state: Dict[str, Any],
    answers: List[Dict[str, str]],
    callbacks: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Submit answers for current round and evaluate them.

    Returns:
    - If all sufficient: complete the interview
    - If ambiguous/invalid: return follow-up questions
    - If should terminate: complete with defaults or error
    """
    current_round = state.get("current_round", 1)
    topic = state["topic"]
    mode = state["mode"]
    duration_months = state["duration_months"]

    # Store current answers
    state["current_answers"] = answers

    # Merge with all answers (update existing or add new)
    answer_map = {a["question_id"]: a for a in state.get("all_answers", [])}
    for a in answers:
        answer_map[a["question_id"]] = a
    state["all_answers"] = list(answer_map.values())

    # Evaluate answers
    evaluation = evaluate_answers(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        questions=state["current_questions"],
        answers=answers,
    )

    # Store evaluations
    eval_map = {e["question_id"]: e for e in state.get("evaluations", [])}
    for e in evaluation.get("evaluations", []):
        eval_map[e["question_id"]] = e
    state["evaluations"] = list(eval_map.values())

    # Track invalid answers
    invalid_ids = evaluation.get("invalid_ids", [])
    ambiguous_ids = evaluation.get("ambiguous_ids", [])

    if invalid_ids:
        state["invalid_count"] = state.get("invalid_count", 0) + len(invalid_ids)
        state["consecutive_invalid"] = state.get("consecutive_invalid", 0) + len(invalid_ids)
        for e in evaluation.get("evaluations", []):
            if e["status"] == "invalid":
                state.setdefault("invalid_history", []).append(e)
    else:
        state["consecutive_invalid"] = 0

    # Check for termination
    termination = check_termination(
        topic=topic,
        total_rounds=current_round,
        invalid_count=state.get("invalid_count", 0),
        consecutive_invalid=state.get("consecutive_invalid", 0),
        invalid_history=state.get("invalid_history", []),
    )

    if termination["should_terminate"]:
        state["is_terminated"] = True
        state["termination_reason"] = termination["reason"]

        if termination["can_continue_with_defaults"]:
            # Complete with available data
            return _complete_interview(state, forced=True)
        else:
            # Cannot continue
            state["error_message"] = termination["reason"]
            return {
                "session_id": state["session_id"],
                "current_round": current_round,
                "is_complete": False,
                "is_terminated": True,
                "termination_reason": termination["reason"],
                "error_message": "인터뷰를 계속할 수 없습니다.",
                "state": state,
            }

    # Check if we need follow-up
    needs_followup = bool(ambiguous_ids or invalid_ids)

    if not needs_followup or current_round >= MAX_ROUNDS:
        # All sufficient or max rounds reached - complete interview
        return _complete_interview(state, forced=(current_round >= MAX_ROUNDS and needs_followup))

    # Generate follow-up questions
    followup_result = generate_followup_questions(
        topic=topic,
        mode=mode,
        current_round=current_round,
        questions=state["current_questions"],
        answers=answers,
        evaluation=evaluation,
    )

    followup_questions = followup_result.get("followup_questions", [])
    warning_message = followup_result.get("warning_message")

    if not followup_questions:
        # No follow-up generated, complete
        return _complete_interview(state, forced=False)

    # Update state for next round
    state["current_round"] = current_round + 1
    state["current_questions"] = followup_questions
    state["warning_message"] = warning_message
    state["followup_count"] = state.get("followup_count", 0) + 1

    return {
        "session_id": state["session_id"],
        "current_round": current_round + 1,
        "max_rounds": MAX_ROUNDS,
        "questions": followup_questions,
        "is_complete": False,
        "is_followup": True,
        "warning_message": warning_message,
        "ambiguous_count": len(ambiguous_ids),
        "invalid_count": len(invalid_ids),
        "state": state,
    }


def _complete_interview(state: Dict[str, Any], forced: bool = False) -> Dict[str, Any]:
    """Complete the interview and compile context."""
    # Compile context
    context_result = compile_interview_context(
        topic=state["topic"],
        mode=state["mode"],
        duration_months=state["duration_months"],
        all_questions=state.get("all_questions", []),
        all_answers=state.get("all_answers", []),
        evaluations=state.get("evaluations", []),
    )

    # Update state
    state["is_complete"] = True
    state["compiled_context"] = context_result["compiled_context"]
    state["key_insights"] = context_result["key_insights"]
    state["extracted_daily_minutes"] = context_result["extracted_daily_minutes"]
    state["extracted_rest_days"] = context_result["extracted_rest_days"]
    state["extracted_intensity"] = context_result["extracted_intensity"]

    # Legacy compatibility
    state["stage_data"] = {
        1: {
            "questions": state.get("all_questions", []),
            "answers": state.get("all_answers", []),
        }
    }
    state["stages_completed"] = [1]
    state["current_stage"] = 1

    return {
        "session_id": state["session_id"],
        "current_round": state.get("current_round", 1),
        "questions": [],
        "is_complete": True,
        "is_followup": False,
        "forced_completion": forced,
        "compiled_context": context_result["compiled_context"],
        "key_insights": context_result["key_insights"],
        "schedule": {
            "daily_minutes": context_result["extracted_daily_minutes"],
            "rest_days": context_result["extracted_rest_days"],
            "intensity": context_result["extracted_intensity"],
        },
        "state": state,
    }
