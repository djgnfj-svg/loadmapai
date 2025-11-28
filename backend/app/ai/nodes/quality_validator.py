import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import QuestionGenerationState
from app.ai.prompts.templates import QUESTION_VALIDATION_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,
    )


def quality_validator(state: QuestionGenerationState) -> QuestionGenerationState:
    """Validate the quality of generated questions."""
    questions = state.get("questions", [])

    # Basic validation without LLM
    issues = []

    if len(questions) < state["num_questions"]:
        issues.append(f"요청된 {state['num_questions']}개 중 {len(questions)}개만 생성됨")

    for i, q in enumerate(questions):
        q_num = i + 1

        if not q.get("question_text"):
            issues.append(f"문제 {q_num}: 문제 텍스트 누락")

        if q.get("question_type") == "multiple_choice":
            options = q.get("options", [])
            if not options or len(options) < 4:
                issues.append(f"문제 {q_num}: 객관식 선택지 부족 (4개 필요)")
            if not q.get("correct_answer"):
                issues.append(f"문제 {q_num}: 정답 누락")

        if not q.get("explanation"):
            issues.append(f"문제 {q_num}: 해설 누락")

    if issues:
        state["validation_passed"] = False
        state["error_message"] = "; ".join(issues)
        state["retry_count"] = state.get("retry_count", 0) + 1
    else:
        state["validation_passed"] = True
        state["error_message"] = None

    return state


def should_retry_question_generation(state: QuestionGenerationState) -> str:
    """Determine if we should retry question generation or proceed."""
    if state.get("validation_passed", False):
        return "save"
    elif state.get("retry_count", 0) < 2:
        return "retry"
    else:
        # Max retries reached, proceed with what we have
        return "save"
