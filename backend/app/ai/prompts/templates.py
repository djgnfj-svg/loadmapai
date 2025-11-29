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

INTERVIEW_QUESTIONS_PROMPT = """당신은 실행 가능한 계획 수립을 돕는 전문 플래너입니다.

사용자가 "{topic}"에 대해 {duration_months}개월 계획을 세우려 합니다.
모드: {mode} ({mode_description})

## 당신의 역할
사용자의 목표를 구체화하고 현실적인 계획을 세울 수 있도록 핵심적인 질문을 합니다.

## 절대 하지 말아야 할 질문 (금지)
다음과 같은 뻔하고 지루한 질문은 절대 하지 마세요:
- "하루에 몇 시간 투자할 수 있나요?" ❌
- "일주일에 쉬는 날이 있나요?" ❌
- "선호하는 학습 강도가 어떻게 되나요?" ❌
- "어느 정도의 페이스로 진행하고 싶으세요?" ❌
- "시간 관리는 어떻게 하고 계세요?" ❌
- 일정/시간/강도 관련 일반적 질문 ❌

이런 질문은 사용자가 알아서 조절할 부분입니다. 로드맵의 내용과 방향을 결정하는 질문만 하세요.

## 좋은 질문의 특징
1. **주제 특화**: "{topic}"에 대해서만 의미 있는 질문
2. **구체적 방향 설정**: 막연한 목표를 구체적 결과물로 좁힘
3. **현실 파악**: 현재 상태와 제약사항 파악
4. **우선순위 도출**: 무엇을 먼저 해야 할지 결정에 도움

## 주제별 질문 예시 (참고용)

### 프로그래밍/개발:
- "어떤 종류의 프로젝트를 만들어보고 싶으세요?"
- "이미 다뤄본 기술 스택이 있나요?"
- "취업 준비인가요, 사이드 프로젝트 목적인가요?"

### 비즈니스/창업:
- "어떤 문제를 해결하는 제품/서비스를 만들고 싶으세요?"
- "타겟 고객층이 누구인가요?"
- "현재 보유한 리소스(자금, 팀, 네트워크)가 있나요?"

### 자격증/시험:
- "목표 시험 일정이 정해져 있나요?"
- "관련 분야 경험이나 배경지식이 있나요?"

### 건강/운동:
- "구체적인 목표 수치가 있나요? (체중, 기록 등)"
- "현재 운동 경험이나 부상 이력이 있나요?"

### 창작/예술:
- "어떤 형태의 결과물을 만들고 싶으세요?"
- "작품을 공개할 계획인가요?"

{mode_specific_guide}

## 출력 형식
다음 JSON 형식으로 정확히 4-5개의 질문을 생성하세요:

{{
    "questions": [
        {{
            "id": "고유_아이디_snake_case",
            "question": "질문 내용",
            "question_type": "single_choice 또는 text",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "placeholder": null,
            "intent": "이 질문으로 파악하려는 것"
        }}
    ]
}}

중요:
- question_type은 "single_choice", "multiple_choice", "text" 중 하나
- id는 영문 snake_case로 고유하게 작성
- 질문은 친근하고 대화하듯이 작성
- **반드시 "{topic}"에 특화된 질문만 생성하세요**
- 시간/강도/일정 관련 일반적 질문은 절대 포함하지 마세요

JSON만 응답하세요."""

INTERVIEW_MODE_LEARNING_GUIDE = """러닝 모드 추가 가이드:
- 선호하는 학습 자료 형태 (영상, 문서, 실습 등) 물어보기
- 이론 vs 실습 비율 선호도 파악"""

INTERVIEW_MODE_PLANNING_GUIDE = """플래닝 모드 추가 가이드:
- 프로젝트/목표의 구체적인 산출물 파악
- 마일스톤이나 중간 목표 설정
- 최종 결과물의 형태 확인"""


# ============ Follow-up Interview Prompts ============

FOLLOWUP_QUESTIONS_PROMPT = """당신은 사용자의 목표를 깊이 이해하기 위한 인터뷰어입니다.

주제: {topic}
기간: {duration_months}개월

## 지금까지의 대화 내용:
{conversation_history}

## 당신의 역할
위 대화를 분석하여 로드맵을 더 정확하게 만들기 위해 필요한 **후속 질문**을 생성하세요.

## 분석 포인트
1. 아직 명확하지 않은 부분이 있는가?
2. 더 구체적인 정보가 필요한 부분은?
3. 사용자의 답변에서 더 깊이 파고들 수 있는 부분은?

## 후속 질문 가이드
- 이전 답변을 참조하여 연결된 질문을 하세요
- "아까 ~라고 하셨는데, 더 구체적으로..."와 같이 자연스럽게 이어가세요
- 단, 이미 충분히 명확한 정보는 다시 묻지 마세요

## 중요: 충분한 정보 수집 여부 판단
만약 로드맵을 만들기에 충분한 정보가 수집되었다면, questions를 빈 배열로 반환하세요.

## 출력 형식
{{
    "analysis": "현재까지 파악된 정보 요약 (2-3문장)",
    "missing_info": ["아직 부족한 정보 1", "아직 부족한 정보 2"],
    "is_sufficient": true/false,
    "questions": [
        {{
            "id": "followup_1",
            "question": "후속 질문 내용",
            "question_type": "single_choice 또는 text",
            "options": ["선택지1", "선택지2"] 또는 null,
            "context": "이 질문을 하는 이유"
        }}
    ]
}}

is_sufficient가 true이면 questions는 빈 배열이어야 합니다.
JSON만 응답하세요."""


# ============ AI-based Roadmap Refinement ============

ROADMAP_REFINEMENT_PROMPT = """당신은 맞춤형 로드맵을 설계하는 전문가입니다.

## 프로젝트 정보
- 주제: {topic}
- 기간: {duration_months}개월
- 모드: {mode}

## 사용자 인터뷰 결과
{interview_context}

## 당신의 역할
위 인터뷰 결과를 바탕으로 **매우 구체적이고 실행 가능한** 로드맵을 생성하세요.

## 중요 지침
1. **구체성**: "~를 학습한다" 대신 "~의 ~기능을 사용하여 ~를 만든다"처럼 구체적으로
2. **연결성**: 각 단계가 이전 단계와 자연스럽게 연결되어야 함
3. **실현 가능성**: 각 일일 태스크는 2-3시간 내에 완료 가능해야 함
4. **맞춤화**: 사용자의 경험 수준, 목표, 제약사항을 반영

## 출력 형식
{{
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (100자 이내, 사용자 목표 반영)",
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "1개월차 목표",
            "description": "이 달에 달성할 구체적 목표",
            "weekly_tasks": [
                {{
                    "week_number": 1,
                    "title": "1주차 과제",
                    "daily_tasks": [
                        {{"day_number": 1, "title": "D1 태스크", "description": "구체적 실행 내용"}},
                        {{"day_number": 2, "title": "D2 태스크", "description": "구체적 실행 내용"}},
                        {{"day_number": 3, "title": "D3 태스크", "description": "구체적 실행 내용"}},
                        {{"day_number": 4, "title": "D4 태스크", "description": "구체적 실행 내용"}},
                        {{"day_number": 5, "title": "D5 태스크", "description": "구체적 실행 내용"}},
                        {{"day_number": 6, "title": "D6 복습/정리", "description": "주간 복습"}},
                        {{"day_number": 7, "title": "D7 휴식/보충", "description": "휴식 또는 밀린 과제"}}
                    ]
                }},
                // week 2, 3, 4...
            ]
        }}
        // month 2, 3...
    ]
}}

참고: 첫 1개월의 첫 2주치만 상세히 생성하세요 (토큰 절약).
나머지는 title만 간략히 채우세요.

JSON만 응답하세요."""

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


# ============ OKR-based Roadmap Generation Prompts ============

ROADMAP_WITH_OKR_PROMPT = """당신은 OKR(Objectives and Key Results) 방법론을 활용하는 전문 로드맵 설계자입니다.

## 프로젝트 정보
- 주제: {topic}
- 기간: {duration_months}개월
- 모드: {mode}

## SMART 인터뷰 결과
{interview_context}

## Key Results (핵심 결과 지표)
{key_results}

## 당신의 역할
위 Key Results를 달성하기 위한 **구체적이고 측정 가능한** 로드맵을 생성하세요.

## OKR 기반 설계 원칙
1. **Objective (목표)**: 각 월별 목표는 Key Results 중 하나와 직접 연결
2. **Key Results 연계**: 모든 주간/일간 태스크는 Key Results 달성에 기여
3. **측정 가능성**: 각 단계 완료 여부를 명확히 판단 가능
4. **70% 원칙**: 야심차지만 70% 달성이 성공으로 간주될 수 있는 수준

## 마일스톤 설정 기준
- 1개월차: 기초 확립 (전체 Key Results의 20% 진행)
- 중간 지점: 핵심 역량 구축 (전체 Key Results의 50% 진행)
- 마지막 달: 완성 및 검증 (전체 Key Results의 100% 목표)

응답 형식 (JSON):
{{
    "objective": "이 로드맵의 핵심 Objective (1문장)",
    "title": "로드맵 제목 (30자 이내)",
    "description": "로드맵 설명 (Key Results 반영, 100자 이내)",
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "1개월차 목표",
            "description": "이 달에 달성할 구체적 목표",
            "key_result_focus": "이 달에 집중할 Key Result",
            "milestone": "이 달 완료 시 확인할 수 있는 구체적 결과물"
        }}
        // ...
    ]
}}

JSON만 응답하세요."""

MONTHLY_WITH_OKR_PROMPT = """주제: {topic}
기간: {duration_months}개월
로드맵 제목: {title}
모드: {mode}

## 사용자 인터뷰 결과
{interview_context}

## Key Results (핵심 결과 지표)
{key_results}

## 웹 검색 컨텍스트 (최신 트렌드/학습 경로)
{search_context}

위 정보를 바탕으로 {duration_months}개월 동안의 월별 학습 목표를 생성해주세요.

## 월별 목표 설계 원칙
1. **Key Results 분배**: 각 Key Result를 월별로 적절히 분배
2. **점진적 난이도**: 기초 → 심화 → 응용 → 완성의 흐름
3. **마일스톤 포함**: 각 월 종료 시 확인 가능한 성과물 명시
4. **검색 결과 반영**: 업계 표준 학습 경로와 추천 자료 고려

응답 형식 (JSON):
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "1개월차 목표 제목",
            "description": "구체적인 학습 목표 설명",
            "key_result_focus": "이 달에 집중할 Key Result",
            "milestone": "월말 확인 가능한 구체적 성과물",
            "success_criteria": "성공 판단 기준 (측정 가능)"
        }},
        ...
    ]
}}

JSON만 응답하세요."""

WEEKLY_WITH_OKR_PROMPT = """주제: {topic}
월별 목표: {monthly_goal_title}
월별 목표 설명: {monthly_goal_description}
이 달의 Key Result 초점: {key_result_focus}
이 달의 마일스톤: {milestone}
해당 월: {month_number}개월차
모드: {mode}

## 사용자 인터뷰 결과
{interview_context}

위 월별 목표와 Key Result를 달성하기 위한 4주간의 주별 학습 과제를 생성해주세요.

## 주간 과제 설계 원칙
1. **Key Result 기여**: 각 주간 과제가 해당 월의 Key Result에 어떻게 기여하는지 명확히
2. **점진적 진행**: 주 1 (25%) → 주 2 (50%) → 주 3 (75%) → 주 4 (100%) 진행률
3. **측정 가능**: 주간 과제 완료 여부를 명확히 판단 가능
4. **복습 포함**: 4주차에는 월간 내용 정리 및 복습 포함

응답 형식 (JSON):
{{
    "weekly_tasks": [
        {{
            "week_number": 1,
            "title": "1주차 과제 제목",
            "description": "구체적인 학습 과제 설명",
            "key_result_contribution": "이 주간 과제가 Key Result에 기여하는 방식",
            "deliverable": "주말에 확인 가능한 구체적 결과물"
        }},
        {{
            "week_number": 2,
            "title": "2주차 과제 제목",
            "description": "구체적인 학습 과제 설명",
            "key_result_contribution": "Key Result 기여 방식",
            "deliverable": "주말 확인 결과물"
        }},
        {{
            "week_number": 3,
            "title": "3주차 과제 제목",
            "description": "구체적인 학습 과제 설명",
            "key_result_contribution": "Key Result 기여 방식",
            "deliverable": "주말 확인 결과물"
        }},
        {{
            "week_number": 4,
            "title": "4주차 과제 제목 (월간 정리)",
            "description": "월간 내용 정리 및 마일스톤 점검",
            "key_result_contribution": "월간 Key Result 달성 확인",
            "deliverable": "월간 마일스톤 완료 확인"
        }}
    ]
}}

JSON만 응답하세요."""

DAILY_WITH_OKR_PROMPT = """주제: {topic}
주별 과제: {weekly_task_title}
주별 과제 설명: {weekly_task_description}
이 주의 Key Result 기여: {key_result_contribution}
이 주의 결과물: {deliverable}
해당 주: {month_number}개월차 {week_number}주차
모드: {mode}

## 사용자 인터뷰 결과
{interview_context}

하루 투자 가능 시간: {daily_time}
휴식일: {rest_days}
학습 강도: {intensity}

위 주별 과제를 완수하기 위한 7일간의 일별 학습 태스크를 생성해주세요.

## 일일 태스크 설계 원칙
1. **시간 준수**: 각 태스크는 하루 {daily_time} 내 완료 가능
2. **구체적 행동**: "~를 학습한다" 대신 "~를 사용하여 ~를 만든다"처럼 행동 중심
3. **검증 가능**: 태스크 완료 여부를 스스로 확인 가능
4. **휴식 반영**: 휴식일({rest_days})에는 복습 또는 가벼운 과제
5. **주간 결과물 연결**: 7일 완료 시 주간 결과물({deliverable}) 완성 가능

## 강도별 가이드
- light: 이론 중심, 가벼운 실습
- moderate: 이론과 실습 균형
- intense: 실습 중심, 깊은 학습

응답 형식 (JSON):
{{
    "daily_tasks": [
        {{
            "day_number": 1,
            "title": "D1 태스크 제목",
            "description": "구체적인 실행 내용 ({daily_time} 내 완료 가능)",
            "checkpoint": "완료 확인 방법"
        }},
        {{
            "day_number": 2,
            "title": "D2 태스크 제목",
            "description": "구체적인 실행 내용",
            "checkpoint": "완료 확인 방법"
        }},
        ...
        {{
            "day_number": 6,
            "title": "D6 복습/정리",
            "description": "주간 내용 복습 및 정리",
            "checkpoint": "복습 완료 확인"
        }},
        {{
            "day_number": 7,
            "title": "D7 휴식/보충",
            "description": "휴식 또는 밀린 과제 처리",
            "checkpoint": "주간 결과물 점검"
        }}
    ]
}}

JSON만 응답하세요."""
