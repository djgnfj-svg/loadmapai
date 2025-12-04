"""Roadmap generation prompts."""

ROADMAP_TITLE_PROMPT = """주제: {topic}
기간: {duration_months}개월
{interview_section}
위 주제에 대한 학습 로드맵의 제목과 설명을 생성해주세요.
인터뷰 정보가 있다면 이를 반영하여 더 개인화된 제목과 설명을 작성해주세요.

응답 형식 (JSON):
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (200자 이내)"
}}

JSON만 응답하세요."""

MONTHLY_GOALS_PROMPT = """주제: {topic}
기간: {duration_months}개월
로드맵 제목: {title}
{interview_section}

원칙:
1. [중요] 정확히 {duration_months}개의 월별 목표만 생성 (초과 금지)
2. 각 월은 이전 월을 기반으로 점진적 심화
3. 인터뷰 정보가 있으면 사용자 수준에 맞게 난이도 조절

응답 형식 (JSON):
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "월 목표 제목",
            "description": "구체적인 학습 목표 설명"
        }}
    ]
}}

JSON만 응답하세요."""

WEEKLY_TASKS_PROMPT = """주제: {topic}
기간: {duration_months}개월
{interview_section}

월별 목표:
{monthly_goals_summary}

원칙:
1. [중요] 정확히 {duration_months}개월치만 생성 (초과 금지)
2. 각 월은 정확히 4주로 구성
3. 주간 과제는 점진적으로 심화

응답 형식 (JSON):
{{
    "weekly_tasks": [
        {{
            "month_number": 1,
            "weeks": [
                {{"week_number": 1, "title": "1주차 과제", "description": "설명"}},
                {{"week_number": 2, "title": "2주차 과제", "description": "설명"}},
                {{"week_number": 3, "title": "3주차 과제", "description": "설명"}},
                {{"week_number": 4, "title": "4주차 과제", "description": "설명"}}
            ]
        }}
    ]
}}

JSON만 응답하세요."""

SINGLE_WEEK_DAILY_TASKS_PROMPT = """주제: {topic}
{interview_section}

현재 주간 정보:
- 주간 목표: {week_title}
- 주간 설명: {week_description}
- 위치: {month_number}개월차 {week_number}주차

원칙:
1. [중요] 정확히 7일(1~7일)만 생성 (초과/미달 금지)
2. 각 일자에 goal(목표)과 tasks(2-3개) 포함
3. 평일(1-5일): 핵심 학습, 주말(6-7일): 복습/정리

응답 형식 (JSON):
{{
    "days": [
        {{
            "day_number": 1,
            "goal": {{"title": "1일차 목표", "description": "핵심 목표 설명"}},
            "tasks": [
                {{"title": "태스크1", "description": "설명"}},
                {{"title": "태스크2", "description": "설명"}}
            ]
        }},
        // 2-5일차: 동일 구조 (평일 학습)
        // 6-7일차: 복습 및 정리
    ]
}}

JSON만 응답하세요."""


def build_interview_section(interview_context: dict) -> str:
    """Build interview section for prompts."""
    if not interview_context:
        return ""

    lines = ["\n사용자 인터뷰 정보:"]

    if interview_context.get("specific_goal"):
        lines.append(f"- 구체적 목표: {interview_context['specific_goal']}")

    if interview_context.get("expected_outcome"):
        lines.append(f"- 기대 결과물: {interview_context['expected_outcome']}")

    if interview_context.get("measurement_criteria"):
        lines.append(f"- 성공 측정 기준: {interview_context['measurement_criteria']}")

    if interview_context.get("current_level"):
        lines.append(f"- 현재 수준: {interview_context['current_level']}")

    resources = interview_context.get("available_resources", {})
    if resources.get("daily_hours"):
        lines.append(f"- 하루 가용 시간: {resources['daily_hours']}시간")
    if resources.get("prior_knowledge"):
        lines.append(f"- 사전 지식: {', '.join(resources['prior_knowledge'])}")

    if interview_context.get("motivation"):
        lines.append(f"- 동기: {interview_context['motivation']}")

    if interview_context.get("learning_style"):
        lines.append(f"- 선호 학습 스타일: {interview_context['learning_style']}")

    if interview_context.get("challenges"):
        lines.append(f"- 예상 어려움: {', '.join(interview_context['challenges'])}")

    return "\n".join(lines) + "\n"
