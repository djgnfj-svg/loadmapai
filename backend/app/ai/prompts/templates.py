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
