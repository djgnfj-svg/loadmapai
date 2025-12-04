"""Interview nodes for SMART-based goal setting."""
import logging

from app.ai.interview_state import InterviewState
from app.ai.llm import invoke_llm_json
from app.ai.prompts.interview_prompts import (
    SMART_QUESTIONS_PROMPT,
    ANSWER_ANALYSIS_PROMPT,
)

logger = logging.getLogger(__name__)


def question_generator(state: InterviewState) -> InterviewState:
    """Generate SMART-based interview questions."""
    prompt = SMART_QUESTIONS_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        state["questions"] = result.get("questions", [])
        state["round"] = 1
        state["needs_followup"] = False
        logger.info(f"[Interview] Generated {len(state['questions'])} questions")
    except Exception as e:
        logger.error(f"[Interview] Failed to generate questions: {e}")
        state["questions"] = _get_default_questions(state["topic"])
        state["round"] = 1
        state["needs_followup"] = False
        state["error_message"] = str(e)

    return state


def answer_analyzer(state: InterviewState) -> InterviewState:
    """Analyze answers and determine if follow-up is needed.

    Uses lower temperature (0.5) for consistent, deterministic analysis results.
    """
    qa_pairs = _format_qa_pairs(state["questions"], state["answers"])

    prompt = ANSWER_ANALYSIS_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
        round=state["round"],
        qa_pairs=qa_pairs,
    )

    try:
        # 분석 작업이므로 낮은 온도(0.5) 사용 - 일관성 중요
        result = invoke_llm_json(prompt, temperature=0.5)

        if state["round"] >= 3:
            state["needs_followup"] = False
        else:
            state["needs_followup"] = result.get("needs_followup", False)

        if state["needs_followup"]:
            state["questions"] = result.get("followup_questions", [])
            state["round"] += 1
            logger.info(f"[Interview] Follow-up needed, round {state['round']}")

        state["interview_context"] = result.get("interview_context", {})
        logger.info(f"[Interview] Analysis complete, needs_followup={state['needs_followup']}")

    except Exception as e:
        logger.error(f"[Interview] Failed to analyze answers: {e}")
        state["needs_followup"] = False
        state["interview_context"] = _build_fallback_context(state)
        state["error_message"] = str(e)

    return state


def _format_qa_pairs(questions: list, answers: list) -> str:
    """Format Q&A pairs for prompt."""
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    lines = []
    for q in questions:
        answer = answer_map.get(q["id"], "무응답")
        if isinstance(answer, list):
            answer = ", ".join(answer)
        lines.append(f"Q [{q['category']}]: {q['question']}")
        lines.append(f"A: {answer}")
        lines.append("")

    return "\n".join(lines)


def _get_default_questions(topic: str) -> list:
    """Return default SMART questions as fallback."""
    return [
        {
            "id": "a1",
            "category": "achievable",
            "question": "현재 관련 지식이나 경험은 어느 정도인가요?",
            "type": "select",
            "options": ["완전 초보 (처음 시작)", "기초 지식 있음", "중급", "고급"],
        },
        {
            "id": "a2",
            "category": "achievable",
            "question": "하루에 학습에 투자할 수 있는 시간은 얼마나 되나요?",
            "type": "select",
            "options": ["30분 이하", "1시간", "2시간", "3시간 이상"],
        },
        {
            "id": "r1",
            "category": "relevant",
            "question": "이 목표를 세운 이유는 무엇인가요?",
            "type": "select",
            "options": [
                "취업/이직 준비",
                "자기 개발",
                "업무에 필요해서",
                "학교/학업 때문에",
                "그냥 관심이 생겨서",
            ],
        },
        {
            "id": "s1",
            "category": "specific",
            "question": f"{topic} 학습에서 가장 중요하게 생각하는 것은 무엇인가요?",
            "type": "select",
            "options": [
                "기초부터 탄탄하게",
                "실전 위주로 빠르게",
                "균형 잡힌 학습",
                "아직 잘 모르겠어요",
            ],
        },
    ]


def _build_fallback_context(state: InterviewState) -> dict:
    """Build fallback interview context from answers."""
    answer_map = {a["question_id"]: a["answer"] for a in state.get("answers", [])}

    return {
        "specific_goal": f"{state['topic']}",
        "expected_outcome": state["topic"],
        "measurement_criteria": "목표 달성",
        "current_level": answer_map.get("a1", "초보"),
        "available_resources": {
            "daily_hours": _parse_daily_hours(answer_map.get("a2", "1시간")),
            "tools": [],
            "prior_knowledge": [],
        },
        "motivation": answer_map.get("r1", "자기 발전"),
        "learning_style": answer_map.get("s1", "균형 잡힌 학습"),
        "challenges": [],
    }


def _parse_daily_hours(answer: str) -> int:
    """Parse daily hours from answer."""
    if "30분" in str(answer):
        return 0.5
    elif "3시간" in str(answer):
        return 3
    elif "2시간" in str(answer):
        return 2
    else:
        return 1
