"""Roadmap generation prompts.

Claude 프롬프트 엔지니어링 베스트 프랙티스 적용:
- XML 태그로 구조화
- 명시적 성공 기준
- 예시 제공 (Multishot)
- Chain of Thought
- 현실적 제약 조건
"""

ROADMAP_TITLE_PROMPT = """당신은 전문 학습 설계 전문가입니다.
학습자의 목표를 분석하여 동기부여가 되는 로드맵 제목과 명확한 설명을 작성합니다.

<project_info>
• 학습 주제: {topic}
• 학습 기간: {duration_months}개월
{interview_section}
</project_info>

<guidelines>
제목 작성:
• 학습 완료 후 얻게 될 핵심 역량을 제목에 반영
• 동기부여가 되면서도 현실적인 목표 제시
• "[기간] + [핵심 역량] + [달성 수준]" 형식 권장

설명 작성:
• 학습 여정의 전체 흐름 요약
• 최종 달성 목표와 기대 성과 명시
• 학습자가 기대할 수 있는 구체적 결과물 언급
</guidelines>

<examples>
좋은 예시:
- 제목: "4주 만에 완성하는 React 실전 개발 역량"
- 설명: "컴포넌트 설계부터 상태관리까지, 실무에서 바로 활용 가능한 React 개발 능력을 단계적으로 습득합니다."

나쁜 예시:
- 제목: "React 공부" (너무 모호)
- 설명: "React를 배웁니다" (구체성 부족)
</examples>

<output_format>
{{
    "title": "동기부여되는 로드맵 제목 (30자 이내)",
    "description": "학습 여정과 최종 달성 목표를 포함한 설명 (200자 이내)"
}}
</output_format>

JSON만 응답하세요."""

MONTHLY_GOALS_PROMPT = """주제: {topic}
기간: {duration_months}개월
로드맵 제목: {title}
{interview_section}

원칙:
1. [중요] 정확히 {duration_months}개의 월별 목표만 생성 (초과 금지)
2. 각 월은 이전 월을 기반으로 점진적 심화
3. 인터뷰 정보가 있으면 사용자 수준에 맞게 난이도 조절

응답 형식 (JSON):
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "월 목표 제목",
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

원칙:
1. [중요] 정확히 {duration_months}개월치만 생성 (초과 금지)
2. 각 월은 정확히 4주로 구성
3. 주간 과제는 점진적으로 심화

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
    ]
}}

JSON만 응답하세요."""

SINGLE_WEEK_DAILY_TASKS_PROMPT = """당신은 현실적이고 달성 가능한 일일 학습 계획을 설계하는 전문가입니다.

<context>
주제: {topic}
현재 위치: {month_number}개월차 {week_number}주차
주간 목표: {week_title}
주간 설명: {week_description}
{interview_section}
</context>

<critical_constraints>
⚠️ 현실성 검증 필수 - 반드시 아래 기준을 지켜주세요:

1. 시간 제약
   - 사용자의 하루 가용 시간을 반드시 확인하세요 (기본: 1-2시간)
   - 각 태스크는 30분-1시간 내 완료 가능해야 합니다
   - 하루 총 학습량은 가용 시간의 80%를 넘지 않아야 합니다

2. 인지 부하 제한
   - 하루에 새로운 개념은 최대 2-3개
   - 암기 항목: 하루 최대 10-15개 (100개 ❌)
   - 실습 과제: 하루 1개의 작은 단위

3. 점진적 진행
   - 1-2일차: 개념 이해 (이론 70% + 실습 30%)
   - 3-4일차: 핵심 실습 (이론 30% + 실습 70%)
   - 5일차: 응용 실습
   - 6-7일차: 복습 및 정리 (가벼운 학습량)
</critical_constraints>

<realistic_examples>
✅ 좋은 예시 (영어 학습, 하루 1시간 기준):
- goal: "필수 동사 10개 학습"
- tasks: ["동사 10개 의미 파악 (20분)", "예문 따라 읽기 (20분)", "간단한 문장 만들기 (20분)"]

❌ 나쁜 예시:
- goal: "기본 어휘 100개 암기" (비현실적 - 하루에 불가능)
- tasks: ["단어 100개 외우기"] (구체성 부족, 시간 초과)

✅ 좋은 예시 (프로그래밍 학습, 하루 2시간 기준):
- goal: "변수와 데이터 타입 이해"
- tasks: ["변수 개념 학습 (30분)", "데이터 타입 종류 파악 (30분)", "간단한 코드 실습 5문제 (60분)"]

❌ 나쁜 예시:
- goal: "Python 기초 문법 전체 마스터" (범위가 너무 넓음)
</realistic_examples>

<output_rules>
1. 정확히 7일(1~7일) 생성
2. 각 일자: goal 1개 + tasks 2-3개
3. 모든 태스크에 예상 소요 시간 명시 권장
4. 평일(1-5일): 핵심 학습
5. 주말(6-7일): 가벼운 복습/정리
</output_rules>

<output_format>
{{
    "days": [
        {{
            "day_number": 1,
            "goal": {{"title": "구체적이고 달성 가능한 목표", "description": "30분-1시간 내 달성 가능한 설명"}},
            "tasks": [
                {{"title": "태스크1 (예상시간)", "description": "구체적인 실행 방법"}},
                {{"title": "태스크2 (예상시간)", "description": "구체적인 실행 방법"}}
            ]
        }}
    ]
}}
</output_format>

<thinking>
응답하기 전에 다음을 확인하세요:
1. 사용자의 하루 가용 시간은 얼마인가?
2. 각 태스크가 해당 시간 내에 현실적으로 완료 가능한가?
3. 하루 학습량이 인지 부하를 초과하지 않는가?
4. 암기 항목이 15개를 초과하지 않는가?
</thinking>

JSON만 응답하세요."""


def build_interview_section(interview_context: dict) -> str:
    """Build interview section for prompts.

    인터뷰 컨텍스트를 프롬프트에 포함할 섹션으로 변환합니다.
    특히 하루 가용 시간 정보를 명확히 전달하여 현실적인 계획 생성을 유도합니다.
    """
    if not interview_context:
        return "\n⚠️ 인터뷰 정보 없음 - 하루 1시간 학습 기준으로 계획하세요.\n"

    lines = ["\n<user_profile>"]

    if interview_context.get("specific_goal"):
        lines.append(f"• 구체적 목표: {interview_context['specific_goal']}")

    if interview_context.get("expected_outcome"):
        lines.append(f"• 기대 결과물: {interview_context['expected_outcome']}")

    if interview_context.get("measurement_criteria"):
        lines.append(f"• 성공 측정 기준: {interview_context['measurement_criteria']}")

    if interview_context.get("current_level"):
        lines.append(f"• 현재 수준: {interview_context['current_level']}")

    resources = interview_context.get("available_resources", {})
    daily_hours = resources.get("daily_hours", 1)
    lines.append(f"• ⏰ 하루 가용 시간: {daily_hours}시간 [중요: 이 시간을 초과하는 계획 금지]")

    if resources.get("prior_knowledge"):
        lines.append(f"• 사전 지식: {', '.join(resources['prior_knowledge'])}")

    if interview_context.get("motivation"):
        lines.append(f"• 동기: {interview_context['motivation']}")

    if interview_context.get("learning_style"):
        lines.append(f"• 선호 학습 스타일: {interview_context['learning_style']}")

    if interview_context.get("challenges"):
        lines.append(f"• 예상 어려움: {', '.join(interview_context['challenges'])}")

    lines.append("</user_profile>\n")
    return "\n".join(lines)
