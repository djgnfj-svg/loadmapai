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

MONTHLY_GOALS_PROMPT = """당신은 10년 이상의 경력을 가진 전문 학습 설계 전문가입니다.
학습자의 목표와 상황을 분석하여 최적의 월간 학습 목표를 설계합니다.

<project_info>
• 학습 주제: {topic}
• 학습 기간: {duration_months}개월
• 로드맵 제목: {title}
{interview_section}
</project_info>

<design_principles>
1. 학습 곡선 설계
   - 1개월차: 기초 체계 구축 (개념 30% + 실습 70%)
   - 중간 월차: 심화 역량 개발 (개념 20% + 실습 60% + 프로젝트 20%)
   - 마지막 월차: 실전 적용 (실습 40% + 프로젝트 60%)

2. 목표 구체성
   - 측정 가능한 성과 목표 포함
   - 해당 월 완료 시 얻게 될 구체적 역량 명시
   - 실무에서 바로 적용 가능한 스킬 중심

3. 연결성
   - 각 월은 이전 월 학습 내용과 자연스럽게 연결
   - 다음 월 학습을 위한 기반 마련
</design_principles>

<topic_examples>
📖 토익 900점 목표 (3개월):
{{
    "monthly_goals": [
        {{"month_number": 1, "title": "토익 기초 문법 및 어휘 완성", "description": "8품사, 시제, 수동태 등 핵심 문법 마스터. 필수 어휘 1000개 학습. 목표: Part 5/6 기초 문제 80% 정답률"}},
        {{"month_number": 2, "title": "RC/LC 파트별 전략 및 집중 훈련", "description": "Part 7 독해 전략, Part 3/4 청취 훈련. 오답 유형 분석. 목표: 각 파트별 모의고사 75% 정답률"}},
        {{"month_number": 3, "title": "실전 모의고사 및 취약점 보완", "description": "주 2회 실전 모의고사, 시간 관리 훈련, 취약 파트 집중 보완. 목표: 900점 달성"}}
    ]
}}

💻 Python 기초 (2개월):
{{
    "monthly_goals": [
        {{"month_number": 1, "title": "Python 기초 문법 및 프로그래밍 사고력 구축", "description": "변수, 자료형, 조건문, 반복문, 함수 마스터. 간단한 프로그램 직접 작성. 목표: 100줄 이상 프로그램 작성 가능"}},
        {{"month_number": 2, "title": "Python 심화 및 실전 프로젝트", "description": "OOP 기초, 파일 처리, 모듈/패키지, 외부 라이브러리 활용. 목표: 개인 미니 프로젝트 완성"}}
    ]
}}

🇯🇵 일본어 N3 (4개월):
{{
    "monthly_goals": [
        {{"month_number": 1, "title": "N3 기초 문법 및 한자 학습", "description": "N3 필수 문법 패턴 50개, 한자 150자 학습. 목표: 기초 문법 테스트 80% 정답률"}},
        {{"month_number": 2, "title": "N3 독해 및 청해 기초", "description": "짧은 문장 독해, 일상 회화 청취 훈련. 목표: 독해/청해 기초 문제 70% 정답률"}},
        {{"month_number": 3, "title": "N3 문법 심화 및 어휘 확장", "description": "복합 문법, 경어 표현, 어휘 2000개. 목표: 문법 심화 문제 75% 정답률"}},
        {{"month_number": 4, "title": "N3 실전 대비 및 모의시험", "description": "실전 모의시험 4회, 취약 영역 집중 보완. 목표: N3 합격"}}
    ]
}}
</topic_examples>

<critical_rules>
⚠️ 필수 준수 사항:
1. [중요] 정확히 {duration_months}개의 월별 목표만 생성 (초과 금지)
2. 각 목표는 해당 월에 실제로 달성 가능한 범위여야 함
3. 제목은 구체적이고 측정 가능해야 함
4. 설명에는 완료 기준/목표 수치를 포함
</critical_rules>

<output_format>
{{
    "monthly_goals": [
        {{
            "month_number": 1,
            "title": "구체적이고 측정 가능한 월 목표",
            "description": "학습 내용, 핵심 스킬, 완료 기준을 포함한 설명 (100자 이내)"
        }}
    ]
}}
</output_format>

JSON만 응답하세요."""

WEEKLY_TASKS_PROMPT = """당신은 10년 이상의 경력을 가진 전문 학습 설계 전문가입니다.
월간 목표를 달성하기 위한 체계적인 4주 학습 커리큘럼을 설계합니다.

<project_info>
• 학습 주제: {topic}
• 학습 기간: {duration_months}개월
{interview_section}
</project_info>

<monthly_goals_context>
{monthly_goals_summary}
</monthly_goals_context>

<prevent_unrealistic_plans>
⚠️ 비현실적 계획 방지 규칙:
1. 각 주차의 학습량은 하루 1-2시간 기준으로 설계
2. 한 주차에 너무 많은 영역을 다루지 마세요 (집중 필요)
3. 월간 목표를 벗어나는 내용 포함 금지
4. 주차별로 명확한 범위 구분 (중복 방지)
</prevent_unrealistic_plans>

<weekly_design_guide>
[1주차 - Foundation Week]
• 목적: 해당 월 학습의 기반 구축
• 내용: 핵심 개념 이해, 기초 실습, 환경 설정
• 난이도: ★☆☆☆☆ ~ ★★☆☆☆

[2주차 - Core Learning Week]
• 목적: 핵심 기능과 패턴 습득
• 내용: 주요 기능 심층 학습, 베스트 프랙티스, 코드 실습
• 난이도: ★★☆☆☆ ~ ★★★☆☆

[3주차 - Advanced Week]
• 목적: 심화 학습 및 응용력 배양
• 내용: 고급 기능, 실제 사용 사례 분석, 복합 실습
• 난이도: ★★★☆☆ ~ ★★★★☆

[4주차 - Integration Week]
• 목적: 종합 적용 및 역량 검증
• 내용: 미니 프로젝트, 학습 내용 통합, 복습
• 난이도: ★★★★☆ ~ ★★★★★
</weekly_design_guide>

<topic_examples>
📖 토익 문법 (월간 목표: "토익 기초 문법 완성"):
{{
    "weekly_tasks": [{{
        "month_number": 1,
        "weeks": [
            {{"week_number": 1, "title": "토익 기초 문법 및 어휘 진단 학습", "description": "8품사 개념, 기본 문장 구조(S+V+O), 시제 기초(현재/과거/미래), 필수 어휘 100개. 완료 기준: Part 5 기초 문제 70% 정답률"}},
            {{"week_number": 2, "title": "시제와 태의 핵심 문법 마스터", "description": "현재완료/과거완료 비교, 수동태 구조, 시제 일치. 실습: Part 5 시제/태 문제 50문제. 완료 기준: 시제 문제 80% 정답률"}},
            {{"week_number": 3, "title": "품사와 수식어 심화 학습", "description": "관계대명사, 분사, 부정사의 역할, 형용사 vs 부사 구별. 실습: Part 6 문단 빈칸 문제. 완료 기준: 품사 문제 80% 정답률"}},
            {{"week_number": 4, "title": "문법 종합 모의고사 및 오답 분석", "description": "Part 5/6 실전 모의고사 2회, 오답 유형 분석, 취약 문법 집중 복습. 완료 기준: 모의고사 85% 정답률"}}
        ]
    }}]
}}

💻 Python 기초 (월간 목표: "Python 기초 문법 완성"):
{{
    "weekly_tasks": [{{
        "month_number": 1,
        "weeks": [
            {{"week_number": 1, "title": "Python 변수와 자료형 학습", "description": "변수 선언, 기본 자료형(int, float, str, bool), 리스트와 튜플, 타입 변환. 실습: 간단한 계산기 프로그램. 완료 기준: 자료형 구별 가능"}},
            {{"week_number": 2, "title": "조건문과 반복문 마스터", "description": "if/elif/else 조건문, for/while 반복문, break/continue, 중첩 반복문. 실습: 숫자 맞추기 게임. 완료 기준: 반복문 활용 가능"}},
            {{"week_number": 3, "title": "함수와 모듈 기초", "description": "함수 정의와 호출, 매개변수와 반환값, 지역/전역 변수, 기본 모듈 사용. 실습: 계산기 함수 모듈화. 완료 기준: 함수 직접 작성 가능"}},
            {{"week_number": 4, "title": "Python 기초 종합 프로젝트", "description": "파일 입출력 기초, 예외 처리, 미니 프로젝트(주소록 또는 할일 관리). 완료 기준: 100줄 이상 프로그램 작성"}}
        ]
    }}]
}}

🇯🇵 일본어 N3 (월간 목표: "N3 문법 기초 완성"):
{{
    "weekly_tasks": [{{
        "month_number": 1,
        "weeks": [
            {{"week_number": 1, "title": "N3 조건/추측 표현 학습", "description": "〜ば, 〜たら, 〜なら 조건 표현, 〜らしい, 〜ようだ 추측 표현. 실습: 예문 작성 20개. 완료 기준: 조건 표현 구별 가능"}},
            {{"week_number": 2, "title": "N3 수수 표현과 경어 기초", "description": "〜てあげる/もらう/くれる 수수 표현, 존경어/겸양어 기초. 실습: 상황별 경어 연습. 완료 기준: 수수 표현 활용"}},
            {{"week_number": 3, "title": "N3 접속 표현과 복합 문법", "description": "〜ながら, 〜たり, 〜ので, 〜のに 접속 표현, 복합 문법 패턴. 실습: JLPT 기출 문법 문제. 완료 기준: 접속 표현 80% 정답률"}},
            {{"week_number": 4, "title": "N3 문법 종합 복습과 모의시험", "description": "1-3주차 문법 종합 복습, N3 문법 모의시험 2회, 오답 분석. 완료 기준: 모의시험 70% 이상"}}
        ]
    }}]
}}
</topic_examples>

<output_requirements>
1. 제목: "[주차 핵심 주제]" 형식으로 명확하게
   ✅ 좋은 예: "토익 기초 문법 및 어휘 진단 학습"
   ❌ 나쁜 예: "2주차 학습" (모호함)

2. 설명: 다음 내용을 모두 포함
   - 학습할 구체적 기술/개념 나열
   - 실습 과제 또는 목표 명시
   - 해당 주 완료 기준 (측정 가능하게)

3. 주차별 범위:
   - 각 주차는 서로 다른 영역을 다뤄야 함
   - 월간 목표 범위 내에서만 설계
</output_requirements>

<critical_rules>
⚠️ 필수 준수 사항:
1. [중요] 정확히 {duration_months}개월치만 생성 (초과 금지)
2. 각 월은 정확히 4주로 구성
3. 주간 과제는 점진적으로 심화
4. 월간 목표를 벗어나는 주제 포함 금지
</critical_rules>

<output_format>
{{
    "weekly_tasks": [
        {{
            "month_number": 1,
            "weeks": [
                {{"week_number": 1, "title": "구체적인 1주차 학습 주제", "description": "학습 내용, 실습 과제, 완료 기준"}},
                {{"week_number": 2, "title": "구체적인 2주차 학습 주제", "description": "학습 내용, 실습 과제, 완료 기준"}},
                {{"week_number": 3, "title": "구체적인 3주차 학습 주제", "description": "학습 내용, 실습 과제, 완료 기준"}},
                {{"week_number": 4, "title": "구체적인 4주차 학습 주제", "description": "학습 내용, 실습 과제, 완료 기준"}}
            ]
        }}
    ]
}}
</output_format>

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
