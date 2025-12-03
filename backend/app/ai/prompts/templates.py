"""Roadmap generation prompts - Simplified for single LLM call per stage."""

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
위 주제에 대해 {duration_months}개월 동안의 월별 학습 목표를 생성해주세요.
각 월의 목표는 이전 월의 학습을 기반으로 점진적으로 심화되어야 합니다.
인터뷰 정보가 있다면 사용자의 현재 수준과 목표에 맞게 난이도를 조절해주세요.

응답 형식 (JSON):
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "1개월차 목표 제목",
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

위의 모든 월({duration_months}개월)에 대해 각각 4주간의 주별 학습 과제를 생성해주세요.
반드시 1개월차부터 {duration_months}개월차까지 모두 포함해야 합니다.
각 주의 과제는 점진적으로 심화되어야 합니다.
인터뷰 정보가 있다면 사용자의 현재 수준에 맞게 난이도를 조절해주세요.

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
        }},
        {{
            "month_number": 2,
            "weeks": [...]
        }}
    ]
}}

JSON만 응답하세요."""

DAILY_TASKS_PROMPT = """주제: {topic}
기간: {duration_months}개월
{interview_section}
주별 과제 목록:
{weekly_tasks_summary}

위의 모든 주별 과제에 대해 각각 7일간의 일별 학습 목표와 태스크를 생성해주세요.
반드시 모든 월의 모든 주차(1-4주)를 포함해야 합니다.

각 일자에는:
1. goal: 그 날의 학습 목표 (접힌 상태에서 볼 수 있는 핵심 목표)
2. tasks: 2-4개의 구체적인 학습 태스크

주말(6-7일차)은 복습 또는 가벼운 과제로 구성해주세요.
인터뷰 정보가 있다면 하루 가용 시간에 맞게 태스크 분량을 조절해주세요.

응답 형식 (JSON):
{{
    "daily_tasks": [
        {{
            "month_number": 1,
            "week_number": 1,
            "days": [
                {{
                    "day_number": 1,
                    "goal": {{"title": "1일차 목표", "description": "오늘 달성할 핵심 목표"}},
                    "tasks": [{{"title": "태스크1", "description": "설명"}}, {{"title": "태스크2", "description": "설명"}}]
                }},
                {{
                    "day_number": 2,
                    "goal": {{"title": "2일차 목표", "description": "오늘 달성할 핵심 목표"}},
                    "tasks": [{{"title": "태스크1", "description": "설명"}}]
                }},
                {{"day_number": 3, "goal": {{...}}, "tasks": [...]}},
                {{"day_number": 4, "goal": {{...}}, "tasks": [...]}},
                {{"day_number": 5, "goal": {{...}}, "tasks": [...]}},
                {{"day_number": 6, "goal": {{...}}, "tasks": [...]}},
                {{"day_number": 7, "goal": {{...}}, "tasks": [...]}}
            ]
        }},
        {{"month_number": 1, "week_number": 2, "days": [...]}},
        {{"month_number": 1, "week_number": 3, "days": [...]}},
        {{"month_number": 1, "week_number": 4, "days": [...]}},
        {{"month_number": 2, "week_number": 1, "days": [...]}},
        ...
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

    if interview_context.get("challenges"):
        lines.append(f"- 예상 어려움: {', '.join(interview_context['challenges'])}")

    return "\n".join(lines) + "\n"
