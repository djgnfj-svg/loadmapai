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
        }},
        ...
    ]
}}

JSON만 응답하세요."""

WEEKLY_TASKS_PROMPT = """주제: {topic}
월별 목표: {monthly_goal_title}
월별 목표 설명: {monthly_goal_description}
해당 월: {month_number}개월차

위 월별 목표를 달성하기 위한 4주간의 주별 학습 과제를 생성해주세요.
각 주의 과제는 점진적으로 심화되어야 합니다.

응답 형식 (JSON):
{{
    "weekly_tasks": [
        {{
            "week_number": 1,
            "title": "1주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 2,
            "title": "2주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 3,
            "title": "3주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 4,
            "title": "4주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }}
    ]
}}

JSON만 응답하세요."""

DAILY_TASKS_PROMPT = """주제: {topic}
주별 과제: {weekly_task_title}
주별 과제 설명: {weekly_task_description}
해당 주: {month_number}개월차 {week_number}주차

위 주별 과제를 완수하기 위한 7일간의 일별 학습 태스크를 생성해주세요.
각 일의 태스크는 구체적이고 실행 가능해야 합니다.
주말(6-7일차)은 복습 또는 가벼운 과제로 구성해주세요.

응답 형식 (JSON):
{{
    "daily_tasks": [
        {{
            "day_number": 1,
            "title": "1일차 태스크 제목",
            "description": "구체적인 학습 내용"
        }},
        ...
        {{
            "day_number": 7,
            "title": "7일차 태스크 제목",
            "description": "주간 복습 또는 가벼운 과제"
        }}
    ]
}}

JSON만 응답하세요."""

VALIDATION_PROMPT = """다음 로드맵 데이터를 검증해주세요:

주제: {topic}
기간: {duration_months}개월

월별 목표 수: {monthly_count}
주별 과제 수: {weekly_count}
일별 태스크 수: {daily_count}

검증 기준:
1. 월별 목표 수가 duration_months와 일치하는가
2. 각 월에 4개의 주별 과제가 있는가
3. 각 주에 7개의 일별 태스크가 있는가
4. 내용이 주제와 관련이 있는가

응답 형식 (JSON):
{{
    "is_valid": true/false,
    "issues": ["문제점1", "문제점2"] // is_valid가 false인 경우만
}}

JSON만 응답하세요."""


# ============ Contextual Roadmap Prompts ============

ROADMAP_TITLE_WITH_CONTEXT_PROMPT = """주제: {topic}
기간: {duration_months}개월
모드: {mode}

사용자 컨텍스트:
{interview_context}

위 정보를 바탕으로 사용자에게 맞춤화된 학습 로드맵의 제목과 설명을 생성해주세요.
컨텍스트를 반영하여 개인화된 내용을 담아주세요.

응답 형식 (JSON):
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (200자 이내, 컨텍스트 반영)"
}}

JSON만 응답하세요."""

ROADMAP_TITLE_WITH_SEARCH_PROMPT = """주제: {topic}
기간: {duration_months}개월
모드: {mode}

사용자 컨텍스트:
{interview_context}

웹 검색을 통해 수집한 최신 학습 정보:
{search_context}

위 정보를 종합하여 사용자에게 맞춤화된 학습 로드맵의 제목과 설명을 생성해주세요.
- 컨텍스트를 반영하여 개인화된 내용 포함
- 웹 검색 결과를 참고하여 최신 트렌드와 권장 학습 경로 반영

응답 형식 (JSON):
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (200자 이내, 개인화 + 최신 정보 반영)"
}}

JSON만 응답하세요."""

MONTHLY_GOALS_WITH_CONTEXT_PROMPT = """주제: {topic}
기간: {duration_months}개월
로드맵 제목: {title}
모드: {mode}

사용자 컨텍스트:
{interview_context}

위 정보와 컨텍스트를 바탕으로 {duration_months}개월 동안의 월별 학습 목표를 생성해주세요.

컨텍스트 반영 사항:
- 사용자의 현재 수준에 맞는 시작점 설정
- 하루 투자 가능 시간을 고려한 적절한 분량
- 사용자의 구체적인 목표를 향한 단계적 진행
- 선호하는 학습 스타일 반영

응답 형식 (JSON):
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "1개월차 목표 제목",
            "description": "구체적인 학습 목표 설명"
        }},
        ...
    ]
}}

JSON만 응답하세요."""

WEEKLY_TASKS_WITH_CONTEXT_PROMPT = """주제: {topic}
월별 목표: {monthly_goal_title}
월별 목표 설명: {monthly_goal_description}
해당 월: {month_number}개월차
모드: {mode}

사용자 컨텍스트:
{interview_context}

위 월별 목표를 달성하기 위한 4주간의 주별 학습 과제를 생성해주세요.
하루 투자 시간과 학습 스타일을 고려하여 적절한 분량으로 구성해주세요.

응답 형식 (JSON):
{{
    "weekly_tasks": [
        {{
            "week_number": 1,
            "title": "1주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 2,
            "title": "2주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 3,
            "title": "3주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }},
        {{
            "week_number": 4,
            "title": "4주차 과제 제목",
            "description": "구체적인 학습 과제 설명"
        }}
    ]
}}

JSON만 응답하세요."""

DAILY_TASKS_WITH_CONTEXT_PROMPT = """주제: {topic}
주별 과제: {weekly_task_title}
주별 과제 설명: {weekly_task_description}
해당 주: {month_number}개월차 {week_number}주차
모드: {mode}

사용자 컨텍스트:
{interview_context}

하루 투자 가능 시간: {daily_time}

위 주별 과제를 완수하기 위한 7일간의 일별 학습 태스크를 생성해주세요.

중요 사항:
- 각 일의 태스크는 사용자의 하루 투자 가능 시간({daily_time})에 맞게 구성
- 태스크는 구체적이고 실행 가능해야 함
- 주말(6-7일차)은 복습 또는 가벼운 과제로 구성
- 사용자의 학습 스타일 선호도 반영

응답 형식 (JSON):
{{
    "daily_tasks": [
        {{
            "day_number": 1,
            "title": "1일차 태스크 제목",
            "description": "구체적인 학습 내용 (투자 시간에 맞는 분량)"
        }},
        ...
        {{
            "day_number": 7,
            "title": "7일차 태스크 제목",
            "description": "주간 복습 또는 가벼운 과제"
        }}
    ]
}}

JSON만 응답하세요."""
