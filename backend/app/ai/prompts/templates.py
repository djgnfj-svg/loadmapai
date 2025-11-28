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


# ============ Quiz Generation Prompts ============

TOPIC_ANALYSIS_PROMPT = """다음 학습 태스크를 분석하고 퀴즈 출제를 위한 정보를 추출해주세요.

로드맵 주제: {roadmap_topic}
월별 목표: {monthly_goal_title}
주별 과제: {weekly_task_title}
일별 태스크: {daily_task_title}
태스크 설명: {daily_task_description}

분석할 내용:
1. 핵심 개념 추출 (3-5개)
2. 난이도 수준 판단 (beginner/intermediate/advanced)
3. 퀴즈 출제 영역 선정 (3-5개)

응답 형식 (JSON):
{{
    "key_concepts": ["개념1", "개념2", "개념3"],
    "difficulty_level": "intermediate",
    "question_focus_areas": ["영역1", "영역2", "영역3"]
}}

JSON만 응답하세요."""

QUESTION_GENERATION_PROMPT = """다음 학습 내용을 바탕으로 {num_questions}개의 퀴즈 문제를 생성해주세요.

학습 주제: {roadmap_topic}
학습 태스크: {daily_task_title}
태스크 설명: {daily_task_description}
핵심 개념: {key_concepts}
난이도: {difficulty_level}
출제 영역: {question_focus_areas}

문제 유형 분배:
- 객관식 (multiple_choice): 약 60%
- 단답형 (short_answer): 약 30%
- 서술형 (essay): 약 10%

주의사항:
1. 코딩 문제는 출제하지 마세요
2. 각 문제는 학습 내용과 직접적으로 관련되어야 합니다
3. 객관식은 4지선다로, 매력적인 오답을 포함해야 합니다
4. 단답형은 명확한 정답이 있어야 합니다
5. 서술형은 이해도를 측정할 수 있는 문제여야 합니다

응답 형식 (JSON):
{{
    "questions": [
        {{
            "question_type": "multiple_choice",
            "question_text": "문제 내용",
            "options": ["A) 선택지1", "B) 선택지2", "C) 선택지3", "D) 선택지4"],
            "correct_answer": "A",
            "explanation": "정답 해설",
            "points": 10
        }},
        {{
            "question_type": "short_answer",
            "question_text": "문제 내용",
            "options": null,
            "correct_answer": "정답",
            "explanation": "정답 해설",
            "points": 15
        }},
        {{
            "question_type": "essay",
            "question_text": "서술형 문제 내용",
            "options": null,
            "correct_answer": "모범답안 요점",
            "explanation": "채점 기준",
            "points": 20
        }}
    ]
}}

JSON만 응답하세요."""

QUESTION_VALIDATION_PROMPT = """다음 퀴즈 문제들을 검증해주세요:

학습 주제: {topic}
문제 수: {question_count}

문제 목록:
{questions_json}

검증 기준:
1. 모든 문제가 학습 주제와 관련이 있는가
2. 객관식 문제에 4개의 선택지가 있는가
3. 정답이 명확하게 지정되어 있는가
4. 해설이 충분히 제공되는가
5. 코딩 문제가 포함되어 있지 않은가

응답 형식 (JSON):
{{
    "is_valid": true/false,
    "issues": ["문제점1", "문제점2"]
}}

JSON만 응답하세요."""


# ============ Grading Prompts ============

ANSWER_GRADING_PROMPT = """다음 답변을 채점해주세요.

문제 유형: {question_type}
문제: {question_text}
{options_text}
정답: {correct_answer}
사용자 답변: {user_answer}

채점 기준:
- multiple_choice: 정답이면 100점, 오답이면 0점
- short_answer: 정답과 일치하면 100점, 의미가 같으면 부분 점수, 완전 오답은 0점
- essay: 핵심 내용 포함 여부에 따라 0-100점 부분 채점

응답 형식 (JSON):
{{
    "is_correct": true/false,
    "score": 85,
    "feedback": "피드백 내용 (왜 맞았는지/틀렸는지, 개선점 등)"
}}

JSON만 응답하세요."""

FEEDBACK_SUMMARY_PROMPT = """다음 퀴즈 결과를 바탕으로 종합 피드백을 작성해주세요.

학습 주제: {topic}
총 문제 수: {total_questions}
맞은 문제 수: {correct_count}
총점: {total_score}/100

각 문제별 결과:
{results_json}

종합 피드백 작성:
1. 전반적인 성취도 평가
2. 잘한 점 (2-3가지)
3. 개선이 필요한 점 (2-3가지)
4. 추가 학습 권장 사항

응답 형식 (JSON):
{{
    "feedback_summary": "종합 피드백 내용 (200자 내외)",
    "strengths": ["잘한 점1", "잘한 점2"],
    "areas_to_improve": ["개선점1", "개선점2"]
}}

JSON만 응답하세요."""


# ============ Interview Prompts ============

INTERVIEW_QUESTIONS_PROMPT = """당신은 맞춤형 학습/프로젝트 로드맵을 생성하기 위해 사용자와 인터뷰하는 AI 코치입니다.

사용자 입력:
- 주제: {topic}
- 모드: {mode} ({mode_description})
- 기간: {duration_months}개월

위 정보를 바탕으로 더 정확하고 맞춤화된 로드맵을 생성하기 위해 필요한 질문을 4-5개 생성해주세요.

질문 작성 가이드:
1. 현재 수준/경험을 파악하는 질문 (필수)
2. 구체적인 목표/성과를 파악하는 질문 (필수)
3. 하루 투자 가능 시간을 파악하는 질문 (필수, id: "daily_time")
4. 쉬는 날을 파악하는 질문 (필수, id: "rest_days")
5. 학습 강도 선호를 파악하는 질문 (필수, id: "intensity")

{mode_specific_guide}

응답 형식 (JSON):
{{
    "questions": [
        {{
            "id": "experience_level",
            "question": "질문 내용",
            "question_type": "single_choice",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "placeholder": null
        }},
        {{
            "id": "daily_time",
            "question": "하루에 얼마나 시간을 투자할 수 있나요?",
            "question_type": "single_choice",
            "options": ["30분 이내", "30분~1시간", "1~2시간", "2시간 이상"],
            "placeholder": null
        }},
        {{
            "id": "rest_days",
            "question": "주중에 학습을 쉬는 날이 있나요?",
            "question_type": "single_choice",
            "options": ["없음 (매일 학습)", "주말만 휴식 (토,일)", "일요일만 휴식", "토요일만 휴식"],
            "placeholder": null
        }},
        {{
            "id": "intensity",
            "question": "원하는 학습 강도는 어느 정도인가요?",
            "question_type": "single_choice",
            "options": ["여유롭게 (light)", "균형있게 (moderate)", "빡세게 (intense)"],
            "placeholder": null
        }},
        {{
            "id": "specific_goal",
            "question": "이 주제를 통해 달성하고 싶은 구체적인 목표가 있나요?",
            "question_type": "text",
            "options": null,
            "placeholder": "예: 포트폴리오용 프로젝트 완성, 자격증 취득, 실무 적용 등"
        }}
    ]
}}

중요:
- question_type은 "single_choice", "multiple_choice", "text" 중 하나
- id는 영문 snake_case로 고유하게 작성
- 질문은 친근하고 대화하듯이 작성
- 5-6개의 질문 생성 (daily_time, rest_days, intensity 필수 포함)

JSON만 응답하세요."""

INTERVIEW_MODE_LEARNING_GUIDE = """러닝 모드 관련 추가 질문 가이드:
- 선호하는 학습 자료 형태 (영상, 문서, 실습 등)
- 퀴즈나 테스트에 대한 선호도
- 이론 vs 실습 비율 선호도"""

INTERVIEW_MODE_PLANNING_GUIDE = """플래닝 모드 관련 추가 질문 가이드:
- 프로젝트/목표의 구체적인 산출물
- 마일스톤이나 중간 목표
- 협업 여부나 피드백 방식"""

ROADMAP_TITLE_WITH_CONTEXT_PROMPT = """주제: {topic}
기간: {duration_months}개월
모드: {mode}

사용자 인터뷰 결과:
{interview_context}

위 정보를 바탕으로 사용자에게 맞춤화된 학습 로드맵의 제목과 설명을 생성해주세요.
인터뷰 결과를 반영하여 개인화된 내용을 담아주세요.

응답 형식 (JSON):
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (200자 이내, 인터뷰 결과 반영)"
}}

JSON만 응답하세요."""

ROADMAP_TITLE_WITH_SEARCH_PROMPT = """주제: {topic}
기간: {duration_months}개월
모드: {mode}

사용자 인터뷰 결과:
{interview_context}

웹 검색을 통해 수집한 최신 학습 정보:
{search_context}

위 정보를 종합하여 사용자에게 맞춤화된 학습 로드맵의 제목과 설명을 생성해주세요.
- 인터뷰 결과를 반영하여 개인화된 내용 포함
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

사용자 인터뷰 결과:
{interview_context}

위 정보와 인터뷰 결과를 바탕으로 {duration_months}개월 동안의 월별 학습 목표를 생성해주세요.

인터뷰 결과 반영 사항:
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

사용자 인터뷰 결과:
{interview_context}

위 월별 목표를 달성하기 위한 4주간의 주별 학습 과제를 생성해주세요.
인터뷰에서 파악한 하루 투자 시간과 학습 스타일을 고려하여 적절한 분량으로 구성해주세요.

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

사용자 인터뷰 결과:
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
