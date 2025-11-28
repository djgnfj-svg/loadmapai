import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import GradingState
from app.ai.prompts.templates import FEEDBACK_SUMMARY_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.5,
    )


def feedback_generator(state: GradingState) -> GradingState:
    """Generate overall feedback summary for the quiz."""
    llm = create_llm()

    # Prepare results JSON for prompt
    results_json = json.dumps([
        {
            "question_id": r["question_id"],
            "is_correct": r["is_correct"],
            "score": r["score"],
            "feedback": r["feedback"],
        }
        for r in state["grading_results"]
    ], ensure_ascii=False, indent=2)

    prompt = FEEDBACK_SUMMARY_PROMPT.format(
        topic=state.get("topic", "퀴즈"),
        total_questions=state["total_questions"],
        correct_count=state["correct_count"],
        total_score=state["total_score"],
        results_json=results_json,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)

        state["feedback_summary"] = result.get("feedback_summary", _generate_default_summary(state))
        state["strengths"] = result.get("strengths", [])
        state["areas_to_improve"] = result.get("areas_to_improve", [])
    except (json.JSONDecodeError, KeyError):
        state["feedback_summary"] = _generate_default_summary(state)
        state["strengths"] = []
        state["areas_to_improve"] = []

    return state


def _generate_default_summary(state: GradingState) -> str:
    """Generate a default feedback summary."""
    score = state.get("total_score", 0)
    correct = state.get("correct_count", 0)
    total = state.get("total_questions", 0)

    if score >= 90:
        level = "훌륭합니다!"
        advice = "이 분야에 대한 이해도가 매우 높습니다."
    elif score >= 70:
        level = "좋습니다!"
        advice = "대부분의 내용을 잘 이해하고 있습니다. 몇 가지 부분만 보완하면 됩니다."
    elif score >= 50:
        level = "보통입니다."
        advice = "기본적인 내용은 이해하고 있지만, 추가 학습이 필요합니다."
    else:
        level = "더 노력이 필요합니다."
        advice = "이 부분을 다시 복습하는 것을 권장합니다."

    return f"{total}문제 중 {correct}문제 정답. 점수: {score}점. {level} {advice}"
