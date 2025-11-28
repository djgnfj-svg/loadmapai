import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import GradingState, GradingResultData
from app.ai.prompts.templates import ANSWER_GRADING_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,
    )


def answer_analyzer(state: GradingState) -> GradingState:
    """Analyze and grade user answers."""
    llm = create_llm()
    grading_results: list[GradingResultData] = []

    for answer in state["answers"]:
        question_type = answer["question_type"]

        # Format options text for multiple choice
        options_text = ""
        if answer.get("options"):
            options_text = "선택지:\n" + "\n".join(answer["options"])

        # Get user answer
        if question_type == "multiple_choice":
            user_answer = answer.get("selected_option", "")
        else:
            user_answer = answer.get("user_answer", "")

        # For multiple choice, do simple matching first
        if question_type == "multiple_choice":
            is_correct = user_answer.upper() == answer.get("correct_answer", "").upper()
            result: GradingResultData = {
                "question_id": answer["question_id"],
                "is_correct": is_correct,
                "score": 100.0 if is_correct else 0.0,
                "feedback": "정답입니다!" if is_correct else f"오답입니다. 정답은 {answer.get('correct_answer')}입니다.",
            }
            grading_results.append(result)
            continue

        # For short_answer and essay, use LLM
        prompt = ANSWER_GRADING_PROMPT.format(
            question_type=question_type,
            question_text=answer["question_text"],
            options_text=options_text,
            correct_answer=answer.get("correct_answer", ""),
            user_answer=user_answer,
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            grading = json.loads(response.content)

            result: GradingResultData = {
                "question_id": answer["question_id"],
                "is_correct": grading.get("is_correct", False),
                "score": float(grading.get("score", 0)),
                "feedback": grading.get("feedback", "채점이 완료되었습니다."),
            }
        except (json.JSONDecodeError, KeyError):
            # Fallback grading for short_answer
            if question_type == "short_answer":
                correct = answer.get("correct_answer", "").lower()
                user = user_answer.lower()
                is_correct = correct in user or user in correct
                result: GradingResultData = {
                    "question_id": answer["question_id"],
                    "is_correct": is_correct,
                    "score": 100.0 if is_correct else 0.0,
                    "feedback": "정답입니다!" if is_correct else f"정답: {answer.get('correct_answer')}",
                }
            else:
                # Essay - give partial credit by default
                result: GradingResultData = {
                    "question_id": answer["question_id"],
                    "is_correct": False,
                    "score": 50.0,  # Default partial credit
                    "feedback": "채점 중 오류가 발생했습니다. 부분 점수가 부여되었습니다.",
                }

        grading_results.append(result)

    state["grading_results"] = grading_results
    return state
