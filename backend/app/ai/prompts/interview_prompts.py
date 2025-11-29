"""AI-driven interview prompts for roadmap generation.

SMART 프레임워크와 OKR 방법론을 활용하여 고품질 맞춤형 로드맵을 생성합니다.
- SMART: Specific, Measurable, Achievable, Relevant, Time-bound
- OKR: Objectives and Key Results
"""

# ============ SMART-Based Interview ============

COMPREHENSIVE_INTERVIEW_PROMPT = """당신은 최고의 목표 설정 코치이자 로드맵 설계 전문가입니다.
SMART 원칙을 활용하여 사용자의 목표를 구체화하고 실현 가능한 로드맵을 설계하세요.

=== 사용자 요청 ===
주제: {topic}
모드: {mode} ({mode_description})
기간: {duration_months}개월

=== 웹 검색 결과 (참고용) ===
{search_context}

=== SMART 프레임워크 기반 필수 수집 정보 ===

**[S] Specific - 구체적 목표** (필수 1개 이상 질문)
수집해야 할 것:
- 무엇을 할 수 있게 되고 싶은가?
- 어떤 결과물/성과를 만들고 싶은가?
- 성공의 모습은 어떤 것인가?

좋은 질문 예시:
- "{topic}"으로 만들고 싶은 결과물이 있나요?
- 어떤 상황에서 "{topic}"을 활용하고 싶으세요?

**[M] Measurable - 측정 가능한 지표** (필수 1개 이상 질문)
수집해야 할 것:
- 성공/실패를 어떻게 판단할 것인가?
- 중간 체크포인트는?
- 구체적인 수치 목표가 있는가?

좋은 질문 예시:
- 목표 달성을 어떻게 확인하실 건가요? (포트폴리오/자격증/취업 등)
- 완성하고 싶은 프로젝트 개수나 목표 점수가 있나요?

**[A] Achievable - 달성 가능성** (필수 1개 이상 질문)
수집해야 할 것:
- 현재 수준/경험은?
- 투입 가능한 시간/자원은?
- 과거 유사한 시도 경험은?

좋은 질문 예시:
- 현재 "{topic}" 관련 경험이 어느 정도 되시나요?
- 이전에 비슷한 것을 시도해 본 적이 있나요?

**[R] Relevant - 연관성/동기** (선택적)
수집해야 할 것:
- 왜 이 목표인가? (진짜 동기)
- 더 큰 계획과의 연결고리는?

좋은 질문 예시:
- 이 목표가 달성되면 무엇이 달라지나요?

**[T] Time-bound - 시간 제약** (이미 {duration_months}개월로 설정됨)
추가 확인:
- 특별한 기한이 있는가? (시험, 취업, 이벤트 등)

좋은 질문 예시:
- 특별히 맞춰야 하는 일정이 있나요? (시험, 면접 등)

=== 주제별 맞춤 질문 예시 ===
{topic_examples}

=== 질문 설계 규칙 ===
1. **반드시 S, M, A 요소에서 각 1개 이상 질문** (최소 3개)
2. 총 4-6개 질문 (너무 많으면 이탈)
3. 객관식 우선 (80%+) - 빠른 응답 유도
4. 선택지는 현실적이고 구체적으로
5. 마지막은 열린 질문 가능 ("추가로 원하시는 것이 있으세요?")

=== 피해야 할 질문 ===
- "하루에 몇 시간 투자하실 건가요?" (너무 뻔함, 나중에 조정 가능)
- "쉬는 날은 언제인가요?" (로드맵과 직접 무관)
- 철학적/추상적 질문
- 이미 웹 검색 결과에서 알 수 있는 일반적인 정보

=== 응답 형식 (JSON) ===
{{
    "smart_coverage": {{
        "specific": true,
        "measurable": true,
        "achievable": true,
        "relevant": false,
        "time_bound": true
    }},
    "questions": [
        {{
            "id": "specific_goal",
            "smart_element": "S",
            "question": "질문 텍스트",
            "question_type": "single_choice",
            "options": ["선택지1", "선택지2", "선택지3", "기타"],
            "intent": "이 질문으로 파악하려는 것"
        }},
        {{
            "id": "measurable_goal",
            "smart_element": "M",
            "question": "측정 가능한 목표 관련 질문",
            "question_type": "single_choice",
            "options": ["선택지1", "선택지2", "선택지3"],
            "intent": "성공 기준 파악"
        }},
        {{
            "id": "achievable_level",
            "smart_element": "A",
            "question": "현재 수준 관련 질문",
            "question_type": "single_choice",
            "options": ["초보", "중급", "고급"],
            "intent": "난이도 조절을 위한 현재 수준 파악"
        }},
        {{
            "id": "open_question",
            "smart_element": null,
            "question": "추가로 고려해야 할 사항이 있나요?",
            "question_type": "text",
            "placeholder": "특별히 원하시는 것이나 제약 사항이 있다면 알려주세요",
            "intent": "추가 요구사항 수집"
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


# ============================================================
# 라운드 분석 프롬프트 (SMART 상태 + Key Results + 상세 로드맵 초안)
# ============================================================

ROUND_ANALYSIS_PROMPT = """당신은 로드맵 설계 전문가이자 솔직한 조언자입니다.
SMART 프레임워크를 기준으로 수집된 정보를 분석하고, OKR 스타일의 Key Results를 도출하세요.

=== 학습 주제 ===
{topic}

=== 기간 ===
{duration_months}개월

=== 현재 라운드 ===
{current_round}라운드 (최소 2라운드, 최대 10라운드)

=== ⚠️ 이전 라운드에서 이미 수집된 SMART 요소 (재질문 금지!) ===
{previous_smart_summary}

⚠️ **중요**: 위에 "수집됨"으로 표시된 요소는 절대 다시 질문하지 마세요!
- 이미 수집된 정보를 유지하고 confidence를 높이세요
- 새로 수집해야 할 요소만 질문하세요

=== 지금까지의 대화 ===
{conversation_history}

=== 1. SMART 상태 분석 ===
각 SMART 요소가 수집되었는지 평가하세요:

**[S] Specific (구체적 목표)**
- 사용자가 원하는 구체적인 결과물/성과가 명확한가?
- 0.0~1.0 신뢰도로 평가

**[M] Measurable (측정 가능)**
- 성공을 어떻게 측정할지 기준이 있는가?
- 포트폴리오, 자격증, 취업 등 구체적 지표가 있는가?

**[A] Achievable (달성 가능)**
- 현재 수준/경험이 파악되었는가?
- 가용 시간/자원이 파악되었는가?

**[R] Relevant (연관성)**
- 왜 이 목표인지 동기가 파악되었는가?
- (선택적 - 없어도 로드맵 생성 가능)

**[T] Time-bound (시간 제한)**
- 특별한 기한이 있는가? (시험, 면접 등)
- (기본적으로 {duration_months}개월로 설정됨)

=== 2. OKR Key Results 도출 ===
수집된 정보를 바탕으로 측정 가능한 3개의 Key Results를 도출하세요:
- KR1: {duration_months}개월 후 "~~~할 수 있다" (역량)
- KR2: "~~~를 완성/획득한다" (결과물)
- KR3: "~~~를 달성한다" (마일스톤)

⚠️ 정보가 부족한 부분은 "???"로 표시

=== 3. 솔직한 피드백 ===
- 달성 가능성을 솔직하게 평가
- 기간이 부족하면 명확히 언급
- 현실적인 조언 제공
- 격려와 긍정적인 면도 언급

=== 4. 능동적 추가 질문 ===
⚠️ **중요: 이미 답변된 내용은 절대 다시 묻지 마세요!**
- 아직 수집되지 않은 SMART 요소 중심으로 질문
- 0-3개의 추가 질문 (정보가 충분하면 0개도 가능)
- 각 질문에 smart_element 태그 필수

=== 5. 상세 로드맵 초안 ===
- **월별**: 핵심 마일스톤 + Key Result 연결
- **주별**: 각 월 4주 테마 (간략하게)
- **일별 예시**: 첫째 주만 상세히 (나머지는 생략)
- 정보 부족한 부분은 "???" 표시

=== 응답 형식 (JSON) ===
{{
    "smart_status": {{
        "specific": {{
            "collected": true,
            "summary": "웹 개발 포트폴리오 제작",
            "confidence": 0.9
        }},
        "measurable": {{
            "collected": true,
            "summary": "프로젝트 2개 완성, GitHub 활성화",
            "confidence": 0.8
        }},
        "achievable": {{
            "collected": false,
            "missing": "현재 프로그래밍 경험 수준",
            "confidence": 0.3
        }},
        "relevant": {{
            "collected": true,
            "summary": "취업 목적",
            "confidence": 0.9
        }},
        "time_bound": {{
            "collected": true,
            "summary": "3개월 후 취업 지원",
            "confidence": 1.0
        }}
    }},
    "key_results": [
        "KR1: Django 기반 웹 프로젝트 독립 개발 가능",
        "KR2: GitHub에 프로젝트 2개 이상 공개",
        "KR3: 기술 면접 핵심 질문 대답 가능"
    ],
    "information_level": "sufficient",
    "feedback": {{
        "honest_opinion": "3개월은 빠듯하지만 매일 2시간씩 투자하시면 충분히 가능합니다. 다만 현재 경험 수준에 따라 진도가 달라질 수 있어요.",
        "encouragement": "취업 목표가 명확하시니 방향성은 좋습니다! Python + Django 조합은 취업 시장에서 수요가 높아요.",
        "suggestions": [
            "하루 2시간 꾸준히 투자하기",
            "프로젝트는 작게 시작해서 점점 확장하기",
            "GitHub 잔디 채우기 습관 들이기"
        ]
    }},
    "proactive_questions": [
        {{
            "id": "achievable_experience",
            "smart_element": "A",
            "question": "현재 프로그래밍 경험이 어느 정도 되시나요?",
            "question_type": "single_choice",
            "options": ["완전 처음", "기초 문법 정도", "간단한 프로젝트 경험 있음", "실무 경험 있음"],
            "purpose": "난이도 조절을 위해 현재 수준 파악 필요"
        }}
    ],
    "draft_roadmap": {{
        "completion_percentage": 65,
        "key_results_focus": ["KR1", "KR2", "KR3"],
        "months": [
            {{
                "month": 1,
                "title": "Python & Django 기초",
                "key_result_focus": "KR1 준비",
                "overview": "Python 문법부터 Django MTV 패턴까지",
                "weeks": [
                    {{
                        "week": 1,
                        "theme": "Python 기초 문법",
                        "daily_example": "Day1: 변수/자료형, Day2: 조건문, Day3: 반복문, Day4: 함수, Day5: 실습, Day6-7: 복습"
                    }},
                    {{
                        "week": 2,
                        "theme": "Python 중급 (클래스, 모듈)"
                    }},
                    {{
                        "week": 3,
                        "theme": "Django 시작"
                    }},
                    {{
                        "week": 4,
                        "theme": "첫 웹앱 완성 (To-Do)"
                    }}
                ]
            }},
            {{
                "month": 2,
                "title": "실전 프로젝트 개발",
                "key_result_focus": "KR1, KR2 진행",
                "overview": "첫 번째 포트폴리오 프로젝트",
                "weeks": [
                    {{"week": 1, "theme": "프로젝트 기획 & DB 설계"}},
                    {{"week": 2, "theme": "핵심 기능 구현"}},
                    {{"week": 3, "theme": "API & 프론트엔드 연동"}},
                    {{"week": 4, "theme": "배포 & GitHub 정리"}}
                ]
            }},
            {{
                "month": 3,
                "title": "포트폴리오 완성 & 취업 준비",
                "key_result_focus": "KR2, KR3 달성",
                "overview": "???",
                "weeks": []
            }}
        ]
    }},
    "should_continue": true,
    "continue_reason": "Achievable 요소 추가 파악 필요"
}}

JSON만 출력하세요."""
