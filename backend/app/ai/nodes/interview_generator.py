import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from typing import List, Dict, Any

from app.config import settings
from app.ai.state import InterviewState, InterviewQuestionData
from app.ai.prompts.templates import (
    INTERVIEW_QUESTIONS_PROMPT,
    INTERVIEW_MODE_LEARNING_GUIDE,
    INTERVIEW_MODE_PLANNING_GUIDE,
)


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


def generate_interview_questions(
    topic: str,
    mode: str,
    duration_months: int,
) -> List[InterviewQuestionData]:
    """Generate personalized interview questions based on topic and mode."""
    llm = create_llm()

    mode_description = "새로운 지식을 학습하고 퀴즈로 검증" if mode == "learning" else "프로젝트/목표 실천 계획 수립"
    mode_specific_guide = INTERVIEW_MODE_LEARNING_GUIDE if mode == "learning" else INTERVIEW_MODE_PLANNING_GUIDE

    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        topic=topic,
        mode=mode,
        mode_description=mode_description,
        duration_months=duration_months,
        mode_specific_guide=mode_specific_guide,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        questions = result.get("questions", [])

        # Validate and transform questions
        validated_questions: List[InterviewQuestionData] = []
        for q in questions:
            validated_questions.append({
                "id": q.get("id", f"q_{len(validated_questions)}"),
                "question": q.get("question", ""),
                "question_type": q.get("question_type", "text"),
                "options": q.get("options"),
                "placeholder": q.get("placeholder"),
            })

        return validated_questions
    except (json.JSONDecodeError, KeyError) as e:
        # Return default questions if AI fails
        return _get_default_questions(topic, mode)


def _get_default_questions(topic: str, mode: str) -> List[InterviewQuestionData]:
    """Return default interview questions as fallback."""
    base_questions: List[InterviewQuestionData] = [
        {
            "id": "experience_level",
            "question": f"{topic}에 대한 현재 경험/지식 수준이 어느 정도인가요?",
            "question_type": "single_choice",
            "options": ["완전 초보 (처음 접함)", "입문자 (기초 지식 있음)", "중급자 (실무 경험 있음)", "고급자 (심화 학습 원함)"],
            "placeholder": None,
        },
        {
            "id": "daily_time",
            "question": "하루에 얼마나 시간을 투자할 수 있나요?",
            "question_type": "single_choice",
            "options": ["30분 이내", "30분~1시간", "1~2시간", "2시간 이상"],
            "placeholder": None,
        },
        {
            "id": "rest_days",
            "question": "주중에 학습을 쉬는 날이 있나요?",
            "question_type": "single_choice",
            "options": ["없음 (매일 학습)", "주말만 휴식 (토,일)", "일요일만 휴식", "토요일만 휴식"],
            "placeholder": None,
        },
        {
            "id": "intensity",
            "question": "원하는 학습 강도는 어느 정도인가요?",
            "question_type": "single_choice",
            "options": ["여유롭게 (light)", "균형있게 (moderate)", "빡세게 (intense)"],
            "placeholder": None,
        },
        {
            "id": "specific_goal",
            "question": "이 주제를 통해 달성하고 싶은 구체적인 목표가 있나요?",
            "question_type": "text",
            "options": None,
            "placeholder": "예: 포트폴리오용 프로젝트 완성, 자격증 취득, 실무 적용 등",
        },
    ]

    if mode == "learning":
        base_questions.append({
            "id": "learning_style",
            "question": "선호하는 학습 방식이 있나요?",
            "question_type": "single_choice",
            "options": ["영상 강의 위주", "문서/책 위주", "직접 실습 위주", "혼합 (다양하게)"],
            "placeholder": None,
        })
    else:
        base_questions.append({
            "id": "deliverable",
            "question": "최종적으로 만들고 싶은 결과물이나 산출물이 있나요?",
            "question_type": "text",
            "options": None,
            "placeholder": "예: 웹 애플리케이션, 포트폴리오 사이트, 분석 리포트 등",
        })

    return base_questions


def format_interview_context(answers: List[Dict[str, str]], questions: List[InterviewQuestionData]) -> str:
    """Format interview answers into context string for roadmap generation."""
    context_lines = []

    # Create a mapping of question_id to question
    question_map = {q["id"]: q for q in questions}

    for answer in answers:
        question_id = answer.get("question_id", "")
        answer_value = answer.get("answer", "")

        if question_id in question_map:
            question = question_map[question_id]
            context_lines.append(f"Q: {question['question']}")
            context_lines.append(f"A: {answer_value}")
            context_lines.append("")

    return "\n".join(context_lines)


def extract_daily_time(answers: List[Dict[str, str]]) -> str:
    """Extract daily time investment from interview answers."""
    for answer in answers:
        if answer.get("question_id") == "daily_time":
            return answer.get("answer", "1~2시간")
    return "1~2시간"  # Default


def extract_daily_available_minutes(answers: List[Dict[str, str]]) -> int:
    """Extract daily available minutes from interview answers."""
    time_mapping = {
        "30분 이내": 30,
        "30분~1시간": 60,
        "1~2시간": 90,
        "2시간 이상": 150,
    }
    daily_time = extract_daily_time(answers)
    return time_mapping.get(daily_time, 60)


def extract_rest_days(answers: List[Dict[str, str]]) -> List[int]:
    """Extract rest days from interview answers.
    Returns list of weekday numbers (0=Sunday, 6=Saturday)
    """
    rest_mapping = {
        "없음 (매일 학습)": [],
        "주말만 휴식 (토,일)": [0, 6],  # Sunday=0, Saturday=6
        "일요일만 휴식": [0],
        "토요일만 휴식": [6],
    }

    for answer in answers:
        if answer.get("question_id") == "rest_days":
            rest_answer = answer.get("answer", "없음 (매일 학습)")
            return rest_mapping.get(rest_answer, [])
    return []  # Default: no rest days


def extract_intensity(answers: List[Dict[str, str]]) -> str:
    """Extract learning intensity from interview answers."""
    intensity_mapping = {
        "여유롭게 (light)": "light",
        "균형있게 (moderate)": "moderate",
        "빡세게 (intense)": "intense",
    }

    for answer in answers:
        if answer.get("question_id") == "intensity":
            intensity_answer = answer.get("answer", "균형있게 (moderate)")
            return intensity_mapping.get(intensity_answer, "moderate")
    return "moderate"  # Default


def extract_schedule_from_answers(answers: List[Dict[str, str]]) -> Dict[str, Any]:
    """Extract complete schedule info from interview answers."""
    return {
        "daily_available_minutes": extract_daily_available_minutes(answers),
        "rest_days": extract_rest_days(answers),
        "intensity": extract_intensity(answers),
    }
