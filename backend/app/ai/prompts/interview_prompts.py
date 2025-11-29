"""AI-driven comprehensive interview prompts for roadmap generation.

The AI generates all necessary questions in a single batch,
focusing on objective (multiple choice) questions for easy user experience.
"""

# ============ AI-Driven Comprehensive Interview ============

COMPREHENSIVE_INTERVIEW_PROMPT = """당신은 최고의 학습 로드맵 생성 전문가입니다.
사용자에게 완벽한 맞춤형 로드맵을 만들기 위해 필요한 모든 정보를 수집해야 합니다.

=== 사용자 요청 ===
주제: {topic}
모드: {mode} ({mode_description})
기간: {duration_months}개월

=== 당신의 임무 ===
이 주제에 대한 최적의 로드맵을 생성하기 위해 반드시 알아야 할 모든 것을 질문하세요.
질문은 대부분 객관식(single_choice)으로 만들어 사용자가 쉽게 답할 수 있게 하세요.

=== 필수 수집 정보 ===
다음 정보는 반드시 수집해야 합니다:

1. **현재 수준** (required_field: "current_level")
   - 이 주제에 대한 사용자의 현재 실력

2. **구체적 목표** (required_field: "specific_goal")
   - "{topic}" 내에서 특히 무엇을 이루고 싶은지
   - 예: "React"라면 → 취업용 포트폴리오? SaaS 개발? 등

3. **학습 가능 시간** (required_field: "daily_time")
   - 하루에 투자 가능한 시간

4. **휴식일** (required_field: "rest_days")
   - 일주일 중 쉬는 날

5. **학습 강도** (required_field: "intensity")
   - 원하는 난이도와 속도

=== 주제별 맞춤 질문 ===
위 필수 정보 외에, "{topic}"에 특화된 추가 질문을 2-3개 생성하세요.
예시:
- 프로그래밍: 선호하는 학습 방식? (강의/책/프로젝트)
- 자격증: 시험 예정일? 이전 시험 경험?
- 언어: 목표 수준? (일상회화/비즈니스/학술)
- 운동: 현재 체력 수준? 부상 이력?
- 악기: 목표 곡? 연주 경험?

=== 질문 작성 규칙 ===
1. 총 6-8개의 질문을 생성하세요
2. 최소 5개는 객관식(single_choice)으로 만드세요
3. 선택지는 구체적이고 실용적으로 작성하세요
4. 사용자가 쉽게 선택할 수 있는 4-5개의 선택지를 제공하세요
5. 질문은 친근하지만 전문적인 톤으로 작성하세요
6. 쓸데없는 철학적 질문 금지 (예: "왜 이게 중요한가요?")
7. 로드맵 생성에 직접 도움이 되는 실용적 질문만

=== 응답 형식 (JSON) ===
{{
    "questions": [
        {{
            "id": "current_level",
            "question": "현재 {topic} 관련 실력은 어느 정도인가요?",
            "question_type": "single_choice",
            "options": ["처음 시작", "기초는 알아요", "어느 정도 해봤어요", "꽤 잘해요"],
            "required_field": "current_level"
        }},
        {{
            "id": "specific_goal",
            "question": "{topic}을(를) 통해 구체적으로 무엇을 하고 싶으신가요?",
            "question_type": "single_choice",
            "options": ["옵션1", "옵션2", "옵션3", "옵션4", "기타 (직접 입력)"],
            "required_field": "specific_goal"
        }},
        {{
            "id": "daily_time",
            "question": "하루에 얼마나 시간을 투자할 수 있나요?",
            "question_type": "single_choice",
            "options": ["30분 이하", "30분~1시간", "1~2시간", "2~3시간", "3시간 이상"],
            "required_field": "daily_time"
        }},
        {{
            "id": "rest_days",
            "question": "일주일 중 쉬는 날은 언제인가요?",
            "question_type": "single_choice",
            "options": ["쉬는 날 없이 매일", "주말(토,일) 휴식", "일요일만 휴식", "토요일만 휴식", "평일 중 하루"],
            "required_field": "rest_days"
        }},
        {{
            "id": "intensity",
            "question": "원하는 학습 강도는요?",
            "question_type": "single_choice",
            "options": ["천천히 꼼꼼하게", "적당한 속도로", "빠르고 도전적으로"],
            "required_field": "intensity"
        }},
        // ... 주제별 맞춤 질문 2-3개 추가
    ]
}}

=== 중요 ===
- 모든 required_field는 반드시 포함되어야 합니다
- "{topic}"에 맞는 현실적이고 구체적인 선택지를 제공하세요
- 사용자가 5분 내에 모든 답변을 완료할 수 있어야 합니다

JSON만 출력하세요."""


# ============ Context Compilation ============

COMPILE_CONTEXT_PROMPT = """당신은 학습 로드맵 생성 전문가입니다.
인터뷰 결과를 로드맵 생성에 최적화된 형태로 정리해야 합니다.

=== 인터뷰 결과 ===
주제: {topic}
모드: {mode}
기간: {duration_months}개월

{interview_qa}

=== 출력 형식 (JSON) ===
{{
    "compiled_context": "로드맵 생성 AI에게 전달할 상세 컨텍스트 (한국어, 마크다운 형식)",
    "key_insights": [
        "핵심 인사이트 1",
        "핵심 인사이트 2",
        "핵심 인사이트 3"
    ],
    "extracted_schedule": {{
        "daily_minutes": 숫자(분 단위),
        "rest_days": [0-6 숫자 배열, 0=월요일, 6=일요일],
        "intensity": "light" | "moderate" | "intense"
    }},
    "roadmap_requirements": {{
        "current_level": "beginner" | "elementary" | "intermediate" | "advanced",
        "specific_goal": "사용자의 구체적 목표",
        "focus_areas": ["집중해야 할 영역들"],
        "learning_style": "사용자 선호 학습 방식",
        "constraints": ["고려해야 할 제약사항들"]
    }}
}}

=== compiled_context 작성 가이드 ===
로드맵 생성 AI가 읽을 것이므로 다음을 명확히 포함:
- 사용자의 현재 수준과 목표
- 구체적으로 달성해야 할 것
- 시간 제약 및 학습 가능 일정
- 특별히 주의할 사항

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
- 로드맵 생성에 필요한 정보가 명확함
- 객관식에서 유효한 선택지를 골랐음
- 텍스트 답변이 구체적이고 실용적임

**2. 애매 (ambiguous)**
- 정보가 있지만 불명확하거나 너무 일반적임
- 예: "앱 만들기" (어떤 앱?), "잘하고 싶어요" (구체적으로 뭘?)
- 예: "적당히", "그냥", "아무거나"

**3. 이상 (invalid)**
- 스팸: "ㅋㅋㅋ", "asdf", 의미없는 문자
- 무관: 질문과 전혀 관련없는 답변
- 적대적: 욕설, 비꼬는 답변
- 너무 짧음: 1-2글자로 성의없는 답변 ("ㅇㅇ", "몰라")

=== 응답 형식 (JSON) ===
{{
    "evaluations": [
        {{
            "question_id": "질문 ID",
            "status": "sufficient" | "ambiguous" | "invalid",
            "extracted_value": "답변에서 추출한 핵심 정보 (있다면)",
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
- 객관식에서 "기타"를 선택하고 내용이 구체적 → sufficient
- 객관식에서 "기타"를 선택하고 내용이 모호 → ambiguous
- 텍스트 답변은 엄격하게 평가 (로드맵 생성에 실제로 도움되는지)

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
1. 이전 답변을 참조하여 더 구체적으로 물어보세요
2. 가능하면 객관식으로 만들어 쉽게 답할 수 있게 하세요
3. 이상한 답변(invalid)에는 친절하지만 단호하게 재질문
4. "아까 X라고 하셨는데, 좀 더 구체적으로..." 형식 권장
5. 질문당 하나의 정보만 물어보세요

=== 이상한 답변 유형별 대응 ===
- too_vague: "좀 더 구체적으로 알려주시면 더 좋은 로드맵을 만들 수 있어요"
- too_short: "조금만 더 자세히 답변해 주세요"
- spam/irrelevant: "질문을 다시 확인해 주세요: [원래 질문]"
- hostile: 무시하고 중립적으로 재질문

=== 응답 형식 (JSON) ===
{{
    "followup_questions": [
        {{
            "id": "원래_질문_id_followup",
            "original_question_id": "원래 질문 ID",
            "question": "후속 질문 텍스트",
            "question_type": "single_choice" | "text",
            "options": ["선택지1", "선택지2", ...],
            "context": "이전에 'X'라고 답변하셨는데...",
            "is_retry": true
        }}
    ],
    "warning_message": "연속으로 이상한 답변 시 표시할 경고 (있다면, 없으면 null)"
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
- 연속 3회 이상 이상한 답변 → 강제 종료 권장
- 전체의 50% 이상이 이상한 답변 → 강제 종료 권장
- 적대적 답변 2회 이상 → 강제 종료 권장

=== 응답 형식 (JSON) ===
{{
    "should_terminate": true | false,
    "reason": "종료 사유 (있다면)",
    "final_warning": "마지막 경고 메시지 (종료 직전이라면)",
    "can_continue_with_defaults": true | false
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
