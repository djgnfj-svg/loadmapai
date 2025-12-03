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

[중요] 정확히 {duration_months}개월치의 월별 학습 목표만 생성하세요.
- 1개월 로드맵이면 month_number: 1만 생성
- 2개월 로드맵이면 month_number: 1, 2만 생성
- 3개월 로드맵이면 month_number: 1, 2, 3만 생성
(이하 동일)

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
        // {duration_months}개월이면 정확히 {duration_months}개의 객체만 포함
    ]
}}

JSON만 응답하세요."""

WEEKLY_TASKS_PROMPT = """주제: {topic}
기간: {duration_months}개월
{interview_section}

월별 목표:
{monthly_goals_summary}

[중요] 위에 나열된 월별 목표에 해당하는 주간 과제만 생성하세요.
- 정확히 {duration_months}개월치만 생성 (더 많이 생성하지 마세요)
- 각 월은 정확히 4주로 구성

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
        }}
        // {duration_months}개월이면 정확히 {duration_months}개의 월 객체만 포함
    ]
}}

JSON만 응답하세요."""

# Legacy prompt - kept for reference but not used in lazy generation
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
        }}
    ]
}}

JSON만 응답하세요."""

# Single week daily tasks generation prompt (for lazy generation)
SINGLE_WEEK_DAILY_TASKS_PROMPT = """주제: {topic}
{interview_section}

현재 주간 정보:
- 주간 목표: {week_title}
- 주간 설명: {week_description}
- 위치: {month_number}개월차 {week_number}주차

위 주간 과제에 대해 정확히 7일(1~7일)의 일별 학습 계획을 생성해주세요.

요구사항:
1. 각 일자에 goal(목표)과 tasks(태스크 2-4개)를 포함
2. 평일(1-5일차): 핵심 학습 내용
3. 주말(6-7일차): 복습 또는 가벼운 과제
4. 정확히 7일치만 생성 (더 많거나 적게 생성하지 마세요)

응답 형식 (JSON):
{{
    "days": [
        {{
            "day_number": 1,
            "goal": {{"title": "1일차 목표", "description": "오늘 달성할 핵심 목표"}},
            "tasks": [
                {{"title": "태스크1", "description": "설명"}},
                {{"title": "태스크2", "description": "설명"}}
            ]
        }},
        {{
            "day_number": 2,
            "goal": {{"title": "2일차 목표", "description": "오늘 달성할 핵심 목표"}},
            "tasks": [
                {{"title": "태스크1", "description": "설명"}},
                {{"title": "태스크2", "description": "설명"}}
            ]
        }},
        {{
            "day_number": 3,
            "goal": {{"title": "3일차 목표", "description": "설명"}},
            "tasks": [{{"title": "태스크1", "description": "설명"}}]
        }},
        {{
            "day_number": 4,
            "goal": {{"title": "4일차 목표", "description": "설명"}},
            "tasks": [{{"title": "태스크1", "description": "설명"}}]
        }},
        {{
            "day_number": 5,
            "goal": {{"title": "5일차 목표", "description": "설명"}},
            "tasks": [{{"title": "태스크1", "description": "설명"}}]
        }},
        {{
            "day_number": 6,
            "goal": {{"title": "6일차 (복습)", "description": "이번 주 학습 복습"}},
            "tasks": [{{"title": "복습", "description": "설명"}}]
        }},
        {{
            "day_number": 7,
            "goal": {{"title": "7일차 (정리)", "description": "주간 마무리"}},
            "tasks": [{{"title": "정리", "description": "설명"}}]
        }}
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
