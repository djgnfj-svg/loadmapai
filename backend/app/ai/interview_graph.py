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
    ROUND_ANALYSIS_PROMPT,
    get_mode_description,
)
from app.ai.prompts.topic_questions import get_topic_examples


# ============ Constants ============
MAX_ROUNDS = 10  # 최대 라운드 (대부분 3-5라운드에서 완료)
MIN_ROUNDS = 2   # 최소 라운드 (충분한 정보 수집을 위해)
MAX_CONSECUTIVE_INVALID = 3


# ============ Question Generation ============

class InterviewGenerationError(Exception):
    """Raised when AI fails to generate interview questions."""
    pass


def generate_interview_questions(
    topic: str,
    mode: str,
    duration_months: int,
    search_context: str = "",
) -> Dict[str, Any]:
    """Generate SMART-based interview questions using AI.

    Args:
        topic: Learning topic
        mode: "learning" or "planning"
        duration_months: Duration in months
        search_context: Web search results for context (optional)

    Returns:
        Dict with questions and smart_coverage

    Raises:
        InterviewGenerationError: If AI fails to generate questions.
    """
    llm = create_llm()

    # Get topic-specific examples
    topic_examples = get_topic_examples(topic)

    prompt = COMPREHENSIVE_INTERVIEW_PROMPT.format(
        topic=topic,
        mode=mode,
        mode_description=get_mode_description(mode),
        duration_months=duration_months,
        search_context=search_context if search_context else "(웹 검색 결과 없음)",
        topic_examples=topic_examples,
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
            # Preserve smart_element if present
            if "smart_element" not in q:
                q["smart_element"] = None

        # Extract SMART coverage from response
        smart_coverage = result.get("smart_coverage", {
            "specific": False,
            "measurable": False,
            "achievable": False,
            "relevant": False,
            "time_bound": True,  # Duration is already set
        })

        return {
            "questions": questions,
            "smart_coverage": smart_coverage,
        }

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


# ============ Round Analysis (SMART-Enhanced) ============

def build_smart_summary(smart_status: Dict[str, Any]) -> str:
    """이전 SMART 상태를 사람이 읽을 수 있는 요약으로 변환."""
    if not smart_status:
        return "(첫 라운드 - 이전 수집 정보 없음)"

    lines = []
    element_names = {
        "specific": "S (Specific, 구체적 목표)",
        "measurable": "M (Measurable, 측정 지표)",
        "achievable": "A (Achievable, 달성 가능성)",
        "relevant": "R (Relevant, 동기/연관성)",
        "time_bound": "T (Time-bound, 기한)",
    }

    for elem, name in element_names.items():
        status = smart_status.get(elem, {})
        if isinstance(status, dict):
            collected = status.get("collected", False)
            confidence = status.get("confidence", 0)
            summary = status.get("summary", "")

            if collected and confidence >= 0.7:
                lines.append(f"✅ {name}: 수집됨 (confidence={confidence:.1f})")
                if summary:
                    lines.append(f"   → {summary[:50]}...")
            elif collected and confidence >= 0.4:
                lines.append(f"🔶 {name}: 부분 수집 (confidence={confidence:.1f})")
                if summary:
                    lines.append(f"   → {summary[:50]}...")
            else:
                lines.append(f"❌ {name}: 미수집")

    return "\n".join(lines) if lines else "(이전 수집 정보 없음)"


def merge_smart_status(
    previous: Dict[str, Any],
    new: Dict[str, Any],
) -> Dict[str, Any]:
    """이전 SMART 상태와 새 상태를 병합 (confidence가 높은 것 유지)."""
    if not previous:
        return new

    merged = {}
    for elem in ["specific", "measurable", "achievable", "relevant", "time_bound"]:
        prev_status = previous.get(elem, {})
        new_status = new.get(elem, {})

        if not isinstance(prev_status, dict):
            prev_status = {}
        if not isinstance(new_status, dict):
            new_status = {}

        prev_conf = prev_status.get("confidence", 0)
        new_conf = new_status.get("confidence", 0)

        # 새 confidence가 더 높거나, 새로 collected된 경우 새 값 사용
        if new_conf > prev_conf or (new_status.get("collected") and not prev_status.get("collected")):
            merged[elem] = new_status
        else:
            # 이전 값 유지하되, 새 정보가 있으면 병합
            merged[elem] = prev_status.copy()
            if new_status.get("summary") and not prev_status.get("summary"):
                merged[elem]["summary"] = new_status["summary"]

    return merged


def analyze_round(
    topic: str,
    mode: str,
    duration_months: int,
    current_round: int,
    all_questions: List[Dict[str, Any]],
    all_answers: List[Dict[str, str]],
    previous_smart_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Analyze current round with SMART framework and provide feedback.

    Enhanced features:
    - SMART status tracking (Specific, Measurable, Achievable, Relevant, Time-bound)
    - OKR Key Results generation
    - Detailed draft roadmap (monthly + weekly + daily example)
    - Honest feedback about difficulties, realistic timelines
    - Proactive questions targeting missing SMART elements
    """
    llm = create_llm(temperature=0.5)  # Balanced for analysis

    # Build conversation history with SMART element tags
    answer_map = {a["question_id"]: a["answer"] for a in all_answers}
    conversation_lines = []

    for q in all_questions:
        answer = answer_map.get(q["id"], "(미응답)")
        smart_tag = f"[{q.get('smart_element', '?')}] " if q.get('smart_element') else ""
        conversation_lines.append(f"{smart_tag}Q: {q['question']}")
        conversation_lines.append(f"A: {answer}")
        conversation_lines.append("")

    conversation_history = "\n".join(conversation_lines)

    # 이전 SMART 상태 요약 생성
    previous_smart_summary = build_smart_summary(previous_smart_status)

    prompt = ROUND_ANALYSIS_PROMPT.format(
        topic=topic,
        duration_months=duration_months,
        current_round=current_round,
        previous_smart_summary=previous_smart_summary,
        conversation_history=conversation_history,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)

        # Ensure all required fields exist with SMART structure
        result.setdefault("smart_status", {
            "specific": {"collected": False, "summary": "", "confidence": 0},
            "measurable": {"collected": False, "summary": "", "confidence": 0},
            "achievable": {"collected": False, "summary": "", "confidence": 0},
            "relevant": {"collected": False, "summary": "", "confidence": 0},
            "time_bound": {"collected": True, "summary": f"{duration_months}개월", "confidence": 1.0},
        })
        result.setdefault("key_results", [])
        result.setdefault("information_level", "minimal")
        result.setdefault("feedback", {
            "honest_opinion": "",
            "encouragement": "",
            "suggestions": []
        })
        result.setdefault("proactive_questions", [])
        result.setdefault("draft_roadmap", {
            "completion_percentage": 0,
            "key_results_focus": [],
            "months": []
        })
        result.setdefault("should_continue", True)
        result.setdefault("continue_reason", "")

        # Assign IDs and smart_element to proactive questions if missing
        for i, q in enumerate(result["proactive_questions"]):
            if "id" not in q:
                q["id"] = f"proactive_{current_round}_{i}"
            q["question_type"] = q.get("question_type", "single_choice")
            q["is_proactive"] = True
            # Keep smart_element from AI response

        return result

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: continue with minimal SMART analysis
        return {
            "smart_status": {
                "specific": {"collected": False, "summary": "", "confidence": 0},
                "measurable": {"collected": False, "summary": "", "confidence": 0},
                "achievable": {"collected": False, "summary": "", "confidence": 0},
                "relevant": {"collected": False, "summary": "", "confidence": 0},
                "time_bound": {"collected": True, "summary": f"{duration_months}개월", "confidence": 1.0},
            },
            "key_results": [],
            "information_level": "minimal",
            "feedback": {
                "honest_opinion": "분석 중 오류가 발생했습니다.",
                "encouragement": "계속 진행해 주세요.",
                "suggestions": []
            },
            "proactive_questions": [],
            "draft_roadmap": {
                "completion_percentage": 0,
                "key_results_focus": [],
                "months": []
            },
            "should_continue": True,
            "continue_reason": "분석 오류로 기본값 적용"
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
    search_context: str = "",
) -> Dict[str, Any]:
    """Start a new interview session and generate SMART-based questions.

    Args:
        topic: Learning topic
        mode: "learning" or "planning"
        duration_months: Duration in months
        user_id: User identifier
        session_id: Optional session ID (generated if not provided)
        callbacks: Optional LangChain callbacks
        search_context: Web search results for context (optional)

    Returns:
        Dict with session info, questions, and initial SMART status
    """
    sid = session_id or str(uuid.uuid4())

    # Generate SMART-based questions
    question_result = generate_interview_questions(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        search_context=search_context,
    )

    questions = question_result["questions"]
    smart_coverage = question_result["smart_coverage"]

    # Initial SMART status (time_bound is already set by duration)
    initial_smart_status = {
        "specific": {"collected": False, "summary": "", "confidence": 0},
        "measurable": {"collected": False, "summary": "", "confidence": 0},
        "achievable": {"collected": False, "summary": "", "confidence": 0},
        "relevant": {"collected": False, "summary": "", "confidence": 0},
        "time_bound": {
            "collected": True,
            "summary": f"{duration_months}개월",
            "confidence": 1.0,
        },
    }

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
        # SMART tracking
        "smart_status": initial_smart_status,
        "smart_coverage": smart_coverage,
        "key_results": [],
        "search_context": search_context,
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
        # SMART-related fields
        "smart_status": initial_smart_status,
        "smart_coverage": smart_coverage,
        "key_results": [],
        "state": state,
    }


def submit_answers(
    state: Dict[str, Any],
    answers: List[Dict[str, str]],
    callbacks: Optional[List[Any]] = None,
    user_wants_complete: bool = False,  # NEW: 사용자가 "완료" 버튼 클릭
) -> Dict[str, Any]:
    """Submit answers for current round with multi-round interview flow.

    New flow:
    1. Evaluate answers (sufficient/ambiguous/invalid)
    2. Analyze round (feedback, proactive questions, draft roadmap)
    3. Decide: continue or complete based on AI + user preference
    4. Return feedback + draft + next questions (if any)

    Args:
        state: Current interview state
        answers: User's answers for current round
        callbacks: Optional LangChain callbacks
        user_wants_complete: If True, user clicked "이 정도면 됐어요" button

    Returns:
        Dict with questions, feedback, draft_roadmap, is_complete, etc.
    """
    current_round = state.get("current_round", 1)
    topic = state["topic"]
    mode = state["mode"]
    duration_months = state["duration_months"]

    # ========== DEBUG LOGGING ==========
    print(f"\n{'='*60}")
    print(f"[INTERVIEW] submit_answers() - Round {current_round}")
    print(f"{'='*60}")
    print(f"[INTERVIEW] Topic: {topic}, Mode: {mode}, Duration: {duration_months}개월")
    print(f"[INTERVIEW] user_wants_complete: {user_wants_complete}")
    print(f"[INTERVIEW] Received answers: {len(answers)}개")
    for ans in answers:
        print(f"  - {ans['question_id']}: {ans['answer'][:50]}..." if len(ans.get('answer', '')) > 50 else f"  - {ans['question_id']}: {ans.get('answer', '')}")

    # State 현황 로깅
    all_q_ids = [q.get("id") for q in state.get("all_questions", [])]
    curr_q_ids = [q.get("id") for q in state.get("current_questions", [])]
    print(f"[INTERVIEW] State 현황:")
    print(f"  - all_questions: {len(all_q_ids)}개 - {all_q_ids}")
    print(f"  - current_questions: {len(curr_q_ids)}개 - {curr_q_ids}")
    print(f"  - all_answers: {len(state.get('all_answers', []))}개")

    # SMART 상태 로깅
    prev_smart = state.get("smart_status", {})
    if prev_smart:
        print(f"[INTERVIEW] 이전 SMART 상태:")
        for elem, status in prev_smart.items():
            if isinstance(status, dict):
                print(f"  - {elem}: collected={status.get('collected')}, confidence={status.get('confidence', 0):.1f}")
    else:
        print(f"[INTERVIEW] 이전 SMART 상태: (없음)")
    print(f"{'='*60}")

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

    # Check for termination (hostile/spam detection)
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
            return _complete_interview(state, forced=True)
        else:
            state["error_message"] = termination["reason"]
            return {
                "session_id": state["session_id"],
                "current_round": current_round,
                "questions": [],  # 빈 질문 리스트 추가
                "is_complete": False,
                "is_terminated": True,
                "termination_reason": termination["reason"],
                "error_message": "인터뷰를 계속할 수 없습니다.",
                "state": state,
            }

    # ===== NEW: Round Analysis =====
    # 분석에 사용할 질문 목록 구성 (중복 체크)
    existing_q_ids = {q.get("id") for q in state.get("all_questions", [])}
    current_qs = state.get("current_questions", [])
    unique_current = [q for q in current_qs if q.get("id") not in existing_q_ids]

    questions_for_analysis = state.get("all_questions", []) + unique_current
    answers_for_analysis = state.get("all_answers", [])

    # 이전 SMART 상태 가져오기
    previous_smart_status = state.get("smart_status", {})

    # ========== DEBUG: analyze_round 호출 전 ==========
    print(f"\n[INTERVIEW] analyze_round() 호출 전:")
    print(f"  - questions_for_analysis: {len(questions_for_analysis)}개")
    q_ids_for_analysis = [q.get("id") for q in questions_for_analysis]
    print(f"  - 질문 ID들: {q_ids_for_analysis}")
    print(f"  - answers_for_analysis: {len(answers_for_analysis)}개")
    print(f"  - previous_smart_status:")
    for elem, status in previous_smart_status.items():
        if isinstance(status, dict):
            print(f"    - {elem}: collected={status.get('collected')}, conf={status.get('confidence', 0):.1f}")

    # 중복 체크 결과
    if len(unique_current) != len(current_qs):
        print(f"  - ⚠️ 중복 제거됨: {len(current_qs)} -> {len(unique_current)}개")
        duplicates = [q.get("id") for q in current_qs if q.get("id") in existing_q_ids]
        print(f"  - 중복된 ID들: {duplicates}")

    round_analysis = analyze_round(
        topic=topic,
        mode=mode,
        duration_months=duration_months,
        current_round=current_round,
        all_questions=questions_for_analysis,
        all_answers=answers_for_analysis,
        previous_smart_status=previous_smart_status,  # NEW: 이전 SMART 상태 전달
    )

    # ========== DEBUG: analyze_round 결과 ==========
    print(f"\n[INTERVIEW] analyze_round() 결과:")
    new_smart = round_analysis.get("smart_status", {})
    print(f"  - AI가 반환한 SMART 상태:")
    for elem, status in new_smart.items():
        if isinstance(status, dict):
            print(f"    - {elem}: collected={status.get('collected')}, confidence={status.get('confidence', 0):.1f}, summary={status.get('summary', '')[:30]}...")

    proactive_qs = round_analysis.get("proactive_questions", [])
    print(f"  - proactive_questions: {len(proactive_qs)}개")
    for pq in proactive_qs:
        print(f"    - [{pq.get('smart_element', '?')}] {pq.get('question', '')[:40]}...")

    draft = round_analysis.get("draft_roadmap", {})
    draft_months = draft.get("months", []) if draft else []
    print(f"  - draft_roadmap: completion={draft.get('completion_percentage', 0)}%, months={len(draft_months)}개")
    print(f"  - information_level: {round_analysis.get('information_level')}")
    print(f"  - should_continue: {round_analysis.get('should_continue')}")

    # SMART 상태 병합 (이전 + 새로운)
    merged_smart_status = merge_smart_status(previous_smart_status, new_smart)
    print(f"\n[INTERVIEW] SMART 상태 병합 결과:")
    for elem, status in merged_smart_status.items():
        if isinstance(status, dict):
            print(f"    - {elem}: collected={status.get('collected')}, confidence={status.get('confidence', 0):.1f}")

    # Store analysis in state (including SMART tracking)
    state["last_feedback"] = round_analysis["feedback"]
    state["last_draft_roadmap"] = round_analysis["draft_roadmap"]
    state["information_level"] = round_analysis["information_level"]
    state["smart_status"] = merged_smart_status  # 병합된 SMART 상태 저장
    state["key_results"] = round_analysis.get("key_results", [])

    # ===== Decide: Complete or Continue =====
    info_level = round_analysis["information_level"]
    ai_recommends_complete = not round_analysis["should_continue"]

    # Force complete if MAX_ROUNDS reached
    if current_round >= MAX_ROUNDS:
        return _complete_interview(state, forced=True, round_analysis=round_analysis)

    # User explicitly wants to complete
    if user_wants_complete and current_round >= MIN_ROUNDS:
        return _complete_interview(state, forced=False, round_analysis=round_analysis)

    # AI says complete AND info is sufficient/complete
    if ai_recommends_complete and info_level in ("sufficient", "complete") and current_round >= MIN_ROUNDS:
        # Return with can_complete flag - let user decide
        pass  # Continue to build response with can_complete=True

    # ===== Build next round questions =====
    next_questions = []

    print(f"\n[INTERVIEW] 다음 라운드 질문 구성:")

    # 1. Follow-up for ambiguous/invalid (if any)
    if ambiguous_ids or invalid_ids:
        print(f"  - followup 대상: ambiguous={ambiguous_ids}, invalid={invalid_ids}")
        followup_result = generate_followup_questions(
            topic=topic,
            mode=mode,
            current_round=current_round,
            questions=state["current_questions"],
            answers=answers,
            evaluation=evaluation,
        )
        followup_qs = followup_result.get("followup_questions", [])
        print(f"  - followup_questions 생성: {len(followup_qs)}개")
        next_questions.extend(followup_qs)

    # 2. Add proactive questions from analysis (중복 필터링 추가)
    proactive_questions = round_analysis.get("proactive_questions", [])

    # 이미 충분히 수집된 SMART 요소 확인
    collected_smart_elements = set()
    current_smart = state.get("smart_status", {})
    for elem, status in current_smart.items():
        if isinstance(status, dict) and status.get("collected") and status.get("confidence", 0) >= 0.7:
            collected_smart_elements.add(elem[0].upper())  # S, M, A, R, T

    print(f"  - 이미 수집된 SMART 요소: {collected_smart_elements}")
    print(f"  - proactive_questions 원본: {len(proactive_questions)}개")

    filtered_proactive = []
    for pq in proactive_questions:
        pq_smart = pq.get("smart_element", "")
        # 이미 수집된 요소에 대한 질문은 스킵
        if pq_smart and pq_smart in collected_smart_elements:
            print(f"    - ⚠️ 스킵 (이미 수집됨): [{pq_smart}] {pq.get('question', '')[:30]}...")
            continue
        filtered_proactive.append(pq)

    print(f"  - proactive_questions 필터링 후: {len(filtered_proactive)}개")

    for pq in filtered_proactive:
        # Convert to standard question format
        next_questions.append({
            "id": pq.get("id", f"proactive_{current_round}_{len(next_questions)}"),
            "question": pq.get("question", ""),
            "question_type": pq.get("question_type", "text"),
            "options": pq.get("options", []),
            "smart_element": pq.get("smart_element"),
            "is_proactive": True,
            "purpose": pq.get("purpose", ""),
        })

    # If no questions and MIN_ROUNDS reached, can complete
    if not next_questions and current_round >= MIN_ROUNDS:
        return _complete_interview(state, forced=False, round_analysis=round_analysis)

    # If no questions but below MIN_ROUNDS, generate generic questions
    if not next_questions and current_round < MIN_ROUNDS:
        print(f"  - MIN_ROUNDS 미달로 generic 질문 생성")
        next_questions = [{
            "id": f"generic_{current_round}_1",
            "question": "로드맵에 추가로 반영했으면 하는 사항이 있으신가요?",
            "question_type": "text",
            "is_proactive": True,
        }]

    # Update state for next round
    print(f"\n[INTERVIEW] State 업데이트:")
    print(f"  - current_round: {current_round} → {current_round + 1}")
    print(f"  - next_questions: {len(next_questions)}개")
    for nq in next_questions:
        print(f"    - [{nq.get('smart_element', '?')}] {nq.get('id')}: {nq.get('question', '')[:40]}...")

    state["current_round"] = current_round + 1
    state["current_questions"] = next_questions
    state["followup_count"] = state.get("followup_count", 0) + 1

    # Add new questions to all_questions
    prev_all_q_count = len(state.get("all_questions", []))
    state["all_questions"] = state.get("all_questions", []) + next_questions
    print(f"  - all_questions: {prev_all_q_count} → {len(state['all_questions'])}개")

    # Determine if user can choose to complete
    can_complete = (
        current_round >= MIN_ROUNDS and
        info_level in ("minimal", "sufficient", "complete")
    )

    # ========== DEBUG: 최종 결과 ==========
    print(f"\n[INTERVIEW] 최종 결과:")
    print(f"  - is_complete: False")
    print(f"  - can_complete: {can_complete}")
    print(f"  - ai_recommends_complete: {ai_recommends_complete}")
    print(f"  - information_level: {info_level}")
    print(f"  - draft_roadmap months: {len(draft_months)}개")
    print(f"{'='*60}\n")

    return {
        "session_id": state["session_id"],
        "current_round": current_round + 1,
        "max_rounds": MAX_ROUNDS,
        "questions": next_questions,
        "is_complete": False,
        "is_followup": bool(ambiguous_ids or invalid_ids),
        # SMART tracking fields
        "smart_status": round_analysis["smart_status"],
        "key_results": round_analysis.get("key_results", []),
        # Feedback and draft roadmap
        "feedback": round_analysis["feedback"],
        "draft_roadmap": round_analysis["draft_roadmap"],
        "information_level": info_level,
        "ai_recommends_complete": ai_recommends_complete,
        "can_complete": can_complete,
        "continue_reason": round_analysis.get("continue_reason", ""),
        # Legacy fields
        "warning_message": None,
        "ambiguous_count": len(ambiguous_ids),
        "invalid_count": len(invalid_ids),
        "state": state,
    }


def _complete_interview(
    state: Dict[str, Any],
    forced: bool = False,
    round_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Complete the interview and compile context.

    Args:
        state: Interview state
        forced: Whether completion was forced (max rounds or termination)
        round_analysis: Last round analysis (for including final feedback)
    """
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

    # Include final feedback, SMART status, key_results if available
    final_feedback = None
    final_draft_roadmap = None
    final_smart_status = state.get("smart_status", {})
    final_key_results = state.get("key_results", [])

    if round_analysis:
        final_feedback = round_analysis.get("feedback")
        final_draft_roadmap = round_analysis.get("draft_roadmap")
        final_smart_status = round_analysis.get("smart_status", final_smart_status)
        final_key_results = round_analysis.get("key_results", final_key_results)
    elif state.get("last_feedback"):
        final_feedback = state.get("last_feedback")
        final_draft_roadmap = state.get("last_draft_roadmap")

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
        # SMART tracking fields
        "smart_status": final_smart_status,
        "key_results": final_key_results,
        # Feedback and draft roadmap
        "feedback": final_feedback,
        "draft_roadmap": final_draft_roadmap,
        "state": state,
    }
