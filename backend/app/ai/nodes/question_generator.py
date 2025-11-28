import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import QuestionGenerationState, QuestionData
from app.ai.prompts.templates import QUESTION_GENERATION_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


def question_generator(state: QuestionGenerationState) -> QuestionGenerationState:
    """Generate quiz questions based on the analyzed topic."""
    llm = create_llm()

    prompt = QUESTION_GENERATION_PROMPT.format(
        roadmap_topic=state["roadmap_topic"],
        daily_task_title=state["daily_task_title"],
        daily_task_description=state["daily_task_description"],
        key_concepts=", ".join(state["key_concepts"]),
        difficulty_level=state["difficulty_level"],
        question_focus_areas=", ".join(state["question_focus_areas"]),
        num_questions=state["num_questions"],
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
        questions = result.get("questions", [])

        # Validate and normalize questions
        normalized_questions = []
        for q in questions:
            question: QuestionData = {
                "question_type": q.get("question_type", "multiple_choice"),
                "question_text": q.get("question_text", ""),
                "options": q.get("options"),
                "correct_answer": q.get("correct_answer"),
                "explanation": q.get("explanation"),
                "points": q.get("points", 10),
            }
            normalized_questions.append(question)

        state["questions"] = normalized_questions

    except (json.JSONDecodeError, KeyError) as e:
        # Generate fallback questions
        state["questions"] = _generate_fallback_questions(state)
        state["error_message"] = f"문제 생성 중 오류 발생: {str(e)}"

    return state


def _generate_fallback_questions(state: QuestionGenerationState) -> list[QuestionData]:
    """Generate fallback questions if AI generation fails."""
    topic = state["daily_task_title"]
    return [
        {
            "question_type": "multiple_choice",
            "question_text": f"{topic}에 대한 이해도를 확인하는 문제입니다. 다음 중 올바른 설명은?",
            "options": [
                "A) 첫 번째 선택지",
                "B) 두 번째 선택지",
                "C) 세 번째 선택지",
                "D) 네 번째 선택지",
            ],
            "correct_answer": "A",
            "explanation": "이 문제에 대한 해설입니다.",
            "points": 10,
        },
        {
            "question_type": "short_answer",
            "question_text": f"{topic}의 핵심 개념을 한 단어로 설명하세요.",
            "options": None,
            "correct_answer": "핵심개념",
            "explanation": "핵심 개념에 대한 설명입니다.",
            "points": 15,
        },
        {
            "question_type": "essay",
            "question_text": f"{topic}에서 배운 내용을 자신의 말로 설명하세요.",
            "options": None,
            "correct_answer": "모범 답안의 핵심 포인트",
            "explanation": "서술형 답안의 채점 기준입니다.",
            "points": 20,
        },
    ]
