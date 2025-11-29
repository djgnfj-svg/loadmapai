"""AI-driven interview prompts for roadmap generation.

AI generates questions freely based on the topic to create the best possible roadmap.
No hardcoded questions - AI decides what's important to ask.
"""

# ============ AI-Driven Interview ============

COMPREHENSIVE_INTERVIEW_PROMPT = """당신은 최고의 로드맵 설계 전문가입니다.
사용자에게 완벽한 맞춤형 로드맵을 만들기 위해 필요한 정보를 수집하세요.

=== 사용자 요청 ===
주제: {topic}
모드: {mode} ({mode_description})
기간: {duration_months}개월

=== 당신의 역할 ===
"{topic}"에 대한 최고의 로드맵을 만들기 위해 정말 중요한 것들만 질문하세요.
당신은 이 분야의 전문가입니다. 무엇을 알아야 좋은 로드맵을 설계할 수 있는지 스스로 판단하세요.

=== 질문 설계 원칙 ===

1. **주제 맞춤 질문**
   - "{topic}"을 잘 가르치려면 무엇을 알아야 할까요?
   - 이 분야에서 초보자가 흔히 하는 실수나 함정은?
   - 사용자의 현재 상황을 파악하기 위해 필요한 정보는?

2. **목표 파악**
   - 같은 주제라도 목표에 따라 로드맵이 완전히 달라집니다
   - 예: "영어" → 여행회화? TOEIC? 비즈니스 영어? 원서 읽기?
   - 예: "프로그래밍" → 취업? 사이드 프로젝트? 자동화?

3. **현실적 제약**
   - 사용자가 실제로 실천할 수 있는 계획을 세우기 위해 필요한 정보
   - 단, 너무 세부적인 스케줄 질문은 피하세요 (AI가 나중에 조정 가능)

=== 피해야 할 질문 ===
- "하루에 몇 시간 투자하실 건가요?" (너무 뻔함)
- "쉬는 날은 언제인가요?" (로드맵과 무관)
- "학습 강도는 어느 정도가 좋을까요?" (사용자가 판단하기 어려움)
- 철학적/추상적 질문 ("왜 이걸 배우고 싶으신가요?")
- 뻔한 질문 (답이 거의 정해져 있는 질문)

=== 좋은 질문 예시 ===
- [프로그래밍] "현재 어떤 프로젝트나 결과물을 만들고 싶으신가요?"
- [프로그래밍] "선호하는 학습 방식이 있나요? (강의/책/직접 만들기)"
- [영어] "영어가 당장 필요한 상황이 있나요? (여행, 업무, 시험 등)"
- [자격증] "시험 일정이 정해져 있나요?"
- [운동] "이전에 시도해봤는데 포기한 경험이 있다면, 이유가 뭐였나요?"
- [악기] "연주하고 싶은 곡이나 장르가 있나요?"

=== 질문 형식 규칙 ===
1. 4-6개의 질문만 생성하세요 (너무 많으면 사용자가 지침)
2. 대부분 객관식(single_choice)으로 만들어 빠르게 답할 수 있게 하세요
3. 선택지는 현실적이고 구체적으로 작성하세요
4. "기타" 선택지를 적절히 활용하세요
5. 정말 열린 답변이 필요한 경우만 텍스트(text) 타입 사용

=== 응답 형식 (JSON) ===
{{
    "questions": [
        {{
            "id": "고유_아이디",
            "question": "질문 텍스트",
            "question_type": "single_choice",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"]
        }},
        {{
            "id": "다른_아이디",
            "question": "주관식이 필요한 질문",
            "question_type": "text",
            "placeholder": "힌트 텍스트"
        }}
    ]
}}

JSON만 출력하세요."""


# ============ Context Compilation ============

COMPILE_CONTEXT_PROMPT = """당신은 로드맵 설계 전문가입니다.
인터뷰 결과를 바탕으로 로드맵 생성 AI에게 전달할 컨텍스트를 작성하세요.

=== 인터뷰 결과 ===
주제: {topic}
모드: {mode}
기간: {duration_months}개월

{interview_qa}

=== 당신의 임무 ===
위 인터뷰 내용을 분석하여:
1. 사용자에게 맞는 로드맵을 설계하기 위한 핵심 정보를 정리
2. 학습 스케줄 추정 (인터뷰에서 힌트를 얻었다면)
3. 로드맵에 반영해야 할 구체적 요구사항 도출

=== 스케줄 추정 가이드 ===
인터뷰에서 시간 관련 정보가 없었다면 합리적으로 추정하세요:
- 직장인/학생이 언급됨 → 하루 1시간 내외
- 풀타임 학습 가능 언급 → 하루 3-4시간
- 기타 → 하루 1-2시간을 기본값으로

휴식일은 특별한 언급이 없으면 주말(토,일)로 설정하세요.

=== 응답 형식 (JSON) ===
{{
    "compiled_context": "로드맵 생성 AI에게 전달할 상세 컨텍스트 (한국어)",
    "key_insights": [
        "핵심 인사이트 1",
        "핵심 인사이트 2",
        "핵심 인사이트 3"
    ],
    "extracted_schedule": {{
        "daily_minutes": 숫자(분 단위, 30-240 사이),
        "rest_days": [0-6 숫자 배열, 0=월요일, 6=일요일],
        "intensity": "light" | "moderate" | "intense"
    }},
    "roadmap_requirements": {{
        "primary_goal": "사용자의 핵심 목표",
        "current_situation": "현재 상황 요약",
        "focus_areas": ["집중해야 할 영역들"],
        "special_considerations": ["특별히 고려할 사항들"]
    }}
}}

JSON만 출력하세요."""


# ============ Batch Answer Evaluation ============

BATCH_ANSWER_EVALUATION_PROMPT = """당신은 인터뷰 답변 품질 평가 전문가입니다.
사용자의 답변들을 평가하여 로드맵 생성에 충분한 정보인지 판단하세요.

=== 인터뷰 컨텍스트 ===
주제: {topic}
모드: {mode}
기간: {duration_months}개월

=== 질문과 답변 ===
{questions_and_answers}

=== 평가 기준 ===

**1. 충분 (sufficient)**
- 로드맵 생성에 도움이 되는 정보가 있음
- 객관식에서 유효한 선택지를 골랐음
- 텍스트 답변이 이해 가능하고 의미가 있음

**2. 애매 (ambiguous)**
- 정보가 있지만 너무 일반적이거나 불명확함
- 예: "그냥 잘하고 싶어요", "아무거나", "적당히"

**3. 이상 (invalid)**
- 스팸: 의미없는 문자 (ㅋㅋ, asdf, 등)
- 무관: 질문과 전혀 관련없는 답변
- 적대적: 욕설, 비꼬는 답변
- 너무 짧음: 1-2글자로 성의없는 답변

=== 응답 형식 (JSON) ===
{{
    "evaluations": [
        {{
            "question_id": "질문 ID",
            "status": "sufficient" | "ambiguous" | "invalid",
            "extracted_value": "답변에서 추출한 핵심 정보",
            "issue": "문제점 설명 (ambiguous/invalid인 경우)",
            "issue_type": null | "too_vague" | "too_short" | "spam" | "irrelevant" | "hostile"
        }}
    ],
    "overall_quality": "good" | "needs_followup" | "problematic",
    "invalid_count": 0,
    "ambiguous_ids": ["애매한 답변의 question_id 목록"],
    "invalid_ids": ["이상한 답변의 question_id 목록"]
}}

=== 중요 ===
- 객관식에서 제공된 선택지를 고른 경우 → sufficient
- 너무 엄격하게 평가하지 마세요. 로드맵 생성에 참고할 수 있으면 OK
- 완벽한 답변을 기대하지 마세요

JSON만 출력하세요."""


# ============ Follow-up Questions Generation ============

FOLLOWUP_QUESTIONS_PROMPT = """당신은 인터뷰 전문가입니다.
애매하거나 이상한 답변에 대해 후속 질문을 생성하세요.

=== 인터뷰 컨텍스트 ===
주제: {topic}
모드: {mode}
현재 라운드: {current_round}/3

=== 후속 질문이 필요한 항목 ===
{items_needing_followup}

=== 후속 질문 작성 규칙 ===
1. 같은 질문을 그대로 반복하지 마세요
2. 선택지를 제공해서 쉽게 답할 수 있게 하세요
3. 이전 답변을 언급하며 부드럽게 다시 물어보세요
4. 꼭 필요한 정보가 아니면 건너뛰어도 됩니다

=== 응답 형식 (JSON) ===
{{
    "followup_questions": [
        {{
            "id": "원래_질문_id_followup",
            "original_question_id": "원래 질문 ID",
            "question": "후속 질문",
            "question_type": "single_choice",
            "options": ["선택지1", "선택지2", "선택지3"],
            "context": "이전 답변 참조 문구",
            "is_retry": true
        }}
    ],
    "warning_message": null
}}

JSON만 출력하세요."""


# ============ Force Termination Check ============

TERMINATION_CHECK_PROMPT = """인터뷰 강제 종료 여부를 판단하세요.

=== 상황 ===
주제: {topic}
총 라운드: {total_rounds}
이상한 답변 누적: {invalid_count}회
연속 이상 답변: {consecutive_invalid}회

=== 이상한 답변 이력 ===
{invalid_history}

=== 판단 기준 ===
- 연속 3회 이상 이상한 답변 → 종료
- 적대적 답변 2회 이상 → 종료
- 그 외에는 웬만하면 계속 진행 (로드맵 생성은 가능)

=== 응답 형식 (JSON) ===
{{
    "should_terminate": true | false,
    "reason": "종료 사유 (있다면)",
    "final_warning": null,
    "can_continue_with_defaults": true
}}

JSON만 출력하세요."""


# ============ Mode Descriptions ============

MODE_DESCRIPTIONS = {
    "learning": "지식 습득과 이해 중심. 개념 학습 → 퀴즈 → 복습 사이클",
    "planning": "실행과 결과물 중심. 프로젝트/목표 달성을 위한 태스크 단위 진행",
}


def get_mode_description(mode: str) -> str:
    """Get description for the given mode."""
    return MODE_DESCRIPTIONS.get(mode, MODE_DESCRIPTIONS["learning"])


# ============ Roadmap Skeleton Generation ============

SKELETON_GENERATION_PROMPT = """당신은 로드맵 구조 설계 전문가입니다.
주어진 주제와 기간을 바탕으로 로드맵의 뼈대(월별/주차별 제목)를 생성하세요.

=== 요청 정보 ===
주제: {topic}
모드: {mode} ({mode_description})
기간: {duration_months}개월

=== 생성 규칙 ===

1. **월별 목표 제목**
   - 각 월에 적합한 학습/실행 단계 제목 생성
   - 자연스러운 진행 순서 (기초 → 심화 → 응용 등)
   - 예: "기초 개념 익히기", "핵심 기술 습득", "실전 프로젝트"

2. **주차별 제목**
   - 해당 월의 목표를 4주로 나눠 구체화
   - 점진적인 난이도 상승
   - 예: "환경 설정", "첫 번째 기능 구현", "테스트 작성"

3. **모드별 특성 반영**
   - learning: 학습, 이해, 복습 중심 용어
   - planning: 실행, 완료, 달성 중심 용어

=== 응답 형식 (JSON) ===
{{
    "months": [
        {{
            "month_number": 1,
            "title": "월별 목표 제목",
            "description": "이 달에 달성할 핵심 목표 한 줄 설명",
            "weeks": [
                {{
                    "week_number": 1,
                    "title": "주차 제목"
                }},
                {{
                    "week_number": 2,
                    "title": "주차 제목"
                }},
                {{
                    "week_number": 3,
                    "title": "주차 제목"
                }},
                {{
                    "week_number": 4,
                    "title": "주차 제목"
                }}
            ]
        }}
    ]
}}

JSON만 출력하세요."""
