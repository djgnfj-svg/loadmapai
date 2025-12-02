"""Roadmap generation prompts - Simplified for single LLM call per stage."""

ROADMAP_TITLE_PROMPT = """주제: {topic}
기간: {duration_months}개월

위 주제에 대한 학습 로드맵의 제목과 설명을 생성해주세요.

응답 형식 (JSON):
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (200자 이내)"
}}

JSON만 응답하세요."""

MONTHLY_GOALS_PROMPT = """주제: {topic}
기간: {duration_months}개월
로드맵 제목: {title}

위 주제에 대해 {duration_months}개월 동안의 월별 학습 목표를 생성해주세요.
각 월의 목표는 이전 월의 학습을 기반으로 점진적으로 심화되어야 합니다.

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

월별 목표:
{monthly_goals_summary}

위의 모든 월({duration_months}개월)에 대해 각각 4주간의 주별 학습 과제를 생성해주세요.
반드시 1개월차부터 {duration_months}개월차까지 모두 포함해야 합니다.
각 주의 과제는 점진적으로 심화되어야 합니다.

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

주별 과제 목록:
{weekly_tasks_summary}

위의 모든 주별 과제에 대해 각각 7일간의 일별 학습 태스크를 생성해주세요.
반드시 모든 월의 모든 주차(1-4주)를 포함해야 합니다.
각 일자에는 2-4개의 구체적인 학습 태스크를 포함해주세요.
주말(6-7일차)은 복습 또는 가벼운 과제로 구성해주세요.

응답 형식 (JSON):
{{
    "daily_tasks": [
        {{
            "month_number": 1,
            "week_number": 1,
            "days": [
                {{"day_number": 1, "tasks": [{{"title": "태스크1", "description": "설명"}}, {{"title": "태스크2", "description": "설명"}}]}},
                {{"day_number": 2, "tasks": [{{"title": "태스크1", "description": "설명"}}, {{"title": "태스크2", "description": "설명"}}]}},
                {{"day_number": 3, "tasks": [...]}},
                {{"day_number": 4, "tasks": [...]}},
                {{"day_number": 5, "tasks": [...]}},
                {{"day_number": 6, "tasks": [...]}},
                {{"day_number": 7, "tasks": [...]}}
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
