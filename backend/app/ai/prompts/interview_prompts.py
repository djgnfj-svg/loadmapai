"""Interview prompts for SMART-based goal setting.

Claude 프롬프트 엔지니어링 베스트 프랙티스 적용:
- XML 태그로 구조화
- 명시적 중복 방지 규칙
- 예시 제공 (Multishot)
- Chain of Thought
"""

SMART_QUESTIONS_PROMPT = """당신은 학습 목표 설정을 돕는 전문 코치입니다.
사용자의 학습 목표를 SMART 프레임워크로 분석하기 위한 질문을 생성해주세요.

<user_input>
목표: "{topic}"
기간: {duration_months}개월
</user_input>

<critical_rules>
⚠️ 중복 방지 - 절대 위반 금지:
1. 목표에 이미 포함된 정보는 다시 묻지 마세요
   - "토익 900점" → 목표 점수 묻지 않음
   - "정보처리기사" → 자격증명 묻지 않음
   - "3개월" → 기간 묻지 않음

2. 사용자가 초보자일 수 있습니다
   - 전문 용어나 세부 영역을 모를 수 있음
   - 먼저 현재 수준을 파악한 후 세부 질문
   - "아직 잘 모르겠어요" 옵션 필수 포함
</critical_rules>

<question_order>
반드시 이 순서로 질문하세요:
1. [achievable] 현재 수준/경험 (선택형 - 가장 먼저!)
2. [achievable] 하루 투자 가능 시간 (선택형)
3. [relevant] 목표를 세운 이유/동기 (선택형)
4. [specific] 구체적 방향 (초보자용 옵션 포함)
</question_order>

<smart_framework>
• Achievable: 현재 수준, 경험, 사용 가능한 시간
• Relevant: 왜 이 목표가 중요한지, 동기
• Specific: 초보자도 선택 가능한 옵션 제공
• Measurable: 목표에 수치가 있으면 생략
• Time-bound: 이미 {duration_months}개월로 설정됨 (생략)
</smart_framework>

<examples>
좋은 질문 예시:
{{
    "id": "a1",
    "category": "achievable",
    "question": "현재 관련 지식이나 경험은 어느 정도인가요?",
    "type": "select",
    "options": ["완전 초보 (처음 시작)", "기초 지식 있음", "중급", "고급"]
}}

나쁜 질문 예시 (피해야 함):
- "목표 점수가 몇 점인가요?" (이미 목표에 포함된 정보)
- "어떤 프레임워크를 사용하실 건가요?" (초보자가 모를 수 있음)
</examples>

<output_format>
{{
    "questions": [
        {{
            "id": "카테고리+번호 (예: a1, s1)",
            "category": "specific | measurable | achievable | relevant",
            "question": "친근하고 대화하는 톤의 질문",
            "type": "text | select | multiselect",
            "options": ["옵션1", "옵션2", "아직 잘 모르겠어요"]
        }}
    ]
}}
</output_format>

<constraints>
• 총 4-5개의 질문만 생성
• 선택형 질문에는 반드시 "아직 잘 모르겠어요" 또는 "처음이라 모르겠어요" 옵션 포함
• 질문은 친근하고 대화하는 톤으로
</constraints>

JSON만 응답하세요."""


ANSWER_ANALYSIS_PROMPT = """당신은 학습 목표 설정을 돕는 전문 코치입니다.
사용자의 답변을 분석하여 추가 질문이 필요한지 판단하고, 최종 인터뷰 컨텍스트를 구성해주세요.

<user_input>
목표: "{topic}"
기간: {duration_months}개월
현재 라운드: {round}/3
</user_input>

<previous_qa>
{qa_pairs}
</previous_qa>

<duplicate_prevention>
⚠️ 절대 중복 금지 - 위 질문들과 유사하거나 중복되는 질문 생성 금지

이미 질문한 내용:
{previous_question_summary}

다음 유형의 질문은 생성하지 마세요:
1. 위에서 이미 물어본 질문과 동일하거나 유사한 질문
2. 목표("{topic}")에 이미 포함된 정보에 대한 질문
3. 사용자가 이미 답변한 내용을 다시 묻는 질문
</duplicate_prevention>

<analysis_criteria>
1. 구체적인 목표가 명확한가? (목표에 이미 포함된 정보 고려)
2. 측정 가능한 성공 기준이 있는가? (목표에 수치가 있으면 이미 충족)
3. 현재 수준과 사용 가능한 시간/자원이 파악되었는가?
4. 목표의 동기와 중요성이 이해되었는가?
</analysis_criteria>

<followup_rules>
후속 질문 생성 규칙:
• needs_followup이 true인 경우에만 followup_questions 포함 (최대 2개)
• 라운드가 3이면 needs_followup은 반드시 false
• 사용자가 초보자인 경우 (현재 수준이 낮거나 "모르겠다"고 답한 경우):
  - 전문적인 세부사항을 묻지 마세요
  - 대신 학습 스타일, 선호도, 제약사항을 물어보세요
• 후속 질문은 이전에 없던 새로운 정보를 얻기 위한 것이어야 함
</followup_rules>

<output_format>
{{
    "needs_followup": true/false,
    "followup_questions": [
        {{
            "id": "f1",
            "category": "specific | measurable | achievable | relevant",
            "question": "이전 질문과 중복되지 않는 새로운 질문",
            "type": "text | select | multiselect",
            "options": ["옵션1", "옵션2"]
        }}
    ],
    "interview_context": {{
        "specific_goal": "구체적 목표 요약",
        "expected_outcome": "기대 결과물",
        "measurement_criteria": "측정 기준",
        "current_level": "현재 수준",
        "available_resources": {{
            "daily_hours": 숫자,
            "tools": ["도구1"],
            "prior_knowledge": ["사전 지식"]
        }},
        "motivation": "동기",
        "learning_style": "선호 학습 스타일",
        "challenges": ["예상 어려움"]
    }}
}}
</output_format>

<thinking>
응답하기 전에 확인하세요:
1. 후속 질문이 이전 질문과 중복되지 않는가?
2. 사용자 수준에 맞는 질문인가?
3. 정말 필요한 정보인가, 아니면 이미 충분한가?
</thinking>

JSON만 응답하세요."""


def format_previous_questions(qa_pairs: list) -> str:
    """Format previous questions for duplicate prevention.

    이전에 했던 질문들을 요약하여 중복 방지에 활용합니다.
    """
    if not qa_pairs:
        return "없음 (첫 번째 라운드)"

    questions = []
    for i, qa in enumerate(qa_pairs, 1):
        q = qa.get("question", "")
        questions.append(f"{i}. {q}")

    return "\n".join(questions)
