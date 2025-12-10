"""Learning mode prompts - 문제 생성, 채점, 피드백

Claude 프롬프트 엔지니어링 베스트 프랙티스 적용:
- XML 태그로 구조화
- 명시적 성공 기준
- 예시 제공 (Multishot)
- Chain of Thought
- 현실적 제약 조건
"""

# ============================================================================
# Phase 1: 일일 학습 커리큘럼 생성 (NEW)
# ============================================================================
LEARNING_DAILY_CURRICULUM_PROMPT = """당신은 체계적인 학습 설계 전문가입니다.
주간 학습 목표를 7일간의 구체적인 일일 학습 커리큘럼으로 분해합니다.

<context>
전체 학습 주제: {topic}
현재 위치: {month_number}개월차 {week_number}주차
학습 기간: {duration_months}개월
주간 학습 제목: {weekly_title}
주간 학습 설명: {weekly_description}
{interview_section}
</context>

<critical_rules>
═══════════════════════════════════════════════════════════
⚠️ 가장 중요한 원칙 - 반드시 준수 ⚠️
═══════════════════════════════════════════════════════════

1. 주간 학습 주제({weekly_title})를 절대 벗어나지 마세요
   - 주간 목표가 "문법"이면 7일 모두 문법 관련 내용만
   - 주간 목표가 "듣기"면 7일 모두 듣기 관련 내용만
   - 주간 목표가 "React Hooks"면 7일 모두 Hooks 관련 내용만

   ❌ 금지 예시:
   - "토익 문법" 주간인데 LC 듣기 내용 포함
   - "Python 기초" 주간인데 Django 웹 프레임워크 내용 포함
   - "N3 문법" 주간인데 한자 암기 내용 포함

2. 매일 배우는 내용을 구체적으로 명시하세요
   ❌ 나쁜 예: "문법 학습", "기초 학습" (너무 모호)
   ✅ 좋은 예: "현재완료 시제 (have/has + p.p.)의 4가지 용법"

3. 7일간 점진적으로 심화되는 구조
   - 1-2일차: 기초 개념 학습
   - 3-4일차: 핵심 내용 심화
   - 5일차: 응용 및 실전 연습
   - 6-7일차: 복습 및 종합 정리
</critical_rules>

<topic_specific_examples>
═══════════════════════════════════════════════════════════
📖 예시 1 - 토익 문법 주간 (weekly_title: "토익 기초 문법 및 어휘 진단 학습")
═══════════════════════════════════════════════════════════
{{
    "daily_curriculum": [
        {{"day": 1, "topic": "8품사 개념과 문장의 기본 구조 (S+V+O)", "focus": ["명사", "동사", "형용사 구별", "기본 문장 패턴"], "difficulty": "기초"}},
        {{"day": 2, "topic": "시제 기초: 현재/과거/미래 시제", "focus": ["시제 표지어 (yesterday, tomorrow 등)", "규칙/불규칙 동사 변화"], "difficulty": "기초"}},
        {{"day": 3, "topic": "현재완료와 과거완료 비교", "focus": ["have/has + p.p.", "had + p.p.", "시간 표현과의 조합"], "difficulty": "중급"}},
        {{"day": 4, "topic": "수동태와 능동태 전환", "focus": ["be + p.p. 구조", "by + 행위자", "문맥에 따른 선택"], "difficulty": "중급"}},
        {{"day": 5, "topic": "관계대명사 (who, which, that)", "focus": ["주격/목적격 관계대명사", "관계절의 역할"], "difficulty": "중급"}},
        {{"day": 6, "topic": "이번 주 문법 종합 복습", "focus": ["1-5일차 핵심 개념 정리", "혼동하기 쉬운 문법 구별"], "difficulty": "복습"}},
        {{"day": 7, "topic": "토익 Part 5 실전 문법 문제 풀이", "focus": ["Part 5 빈칸 채우기 유형", "시간 관리 연습"], "difficulty": "복습"}}
    ]
}}

═══════════════════════════════════════════════════════════
💻 예시 2 - Python 기초 주간 (weekly_title: "Python 변수와 자료형 학습")
═══════════════════════════════════════════════════════════
{{
    "daily_curriculum": [
        {{"day": 1, "topic": "변수 선언과 기본 데이터 타입 (int, float, str, bool)", "focus": ["변수 명명 규칙", "타입 확인 type()", "타입 변환"], "difficulty": "기초"}},
        {{"day": 2, "topic": "문자열(str) 다루기", "focus": ["문자열 인덱싱/슬라이싱", "f-string 포매팅", "주요 메서드 (split, join, strip)"], "difficulty": "기초"}},
        {{"day": 3, "topic": "리스트(list)와 튜플(tuple)", "focus": ["리스트 CRUD 연산", "mutable vs immutable", "리스트 컴프리헨션"], "difficulty": "중급"}},
        {{"day": 4, "topic": "딕셔너리(dict)와 집합(set)", "focus": ["key-value 구조", "딕셔너리 메서드", "집합 연산 (합집합, 교집합)"], "difficulty": "중급"}},
        {{"day": 5, "topic": "자료형 간 변환과 활용", "focus": ["타입 캐스팅", "중첩 자료구조", "실전 데이터 처리 예제"], "difficulty": "중급"}},
        {{"day": 6, "topic": "이번 주 Python 자료형 복습", "focus": ["1-5일차 핵심 개념", "자주 하는 실수 정리"], "difficulty": "복습"}},
        {{"day": 7, "topic": "자료형 활용 미니 프로젝트", "focus": ["간단한 데이터 처리 프로그램 작성"], "difficulty": "복습"}}
    ]
}}

═══════════════════════════════════════════════════════════
🇯🇵 예시 3 - 일본어 N3 문법 주간 (weekly_title: "N3 조건/추측 표현 학습")
═══════════════════════════════════════════════════════════
{{
    "daily_curriculum": [
        {{"day": 1, "topic": "조건 표현 기초: 〜ば (가정 조건)", "focus": ["ば형 활용법", "〜ば〜ほど 구문", "가정 조건의 뉘앙스"], "difficulty": "기초"}},
        {{"day": 2, "topic": "조건 표현: 〜たら (시간적 조건)", "focus": ["たら형 활용법", "〜ば와의 차이점", "완료 후 상황 표현"], "difficulty": "기초"}},
        {{"day": 3, "topic": "조건 표현: 〜なら (상황 가정)", "focus": ["なら의 용법", "상대방 말 받기", "조언/의견 제시"], "difficulty": "중급"}},
        {{"day": 4, "topic": "추측 표현: 〜らしい, 〜ようだ", "focus": ["전문/추측의 뉘앙스 차이", "근거 있는 추측 표현"], "difficulty": "중급"}},
        {{"day": 5, "topic": "추측 표현: 〜そうだ (양태/전문)", "focus": ["양태의 そうだ vs 전문의 そうだ", "동사/형용사 접속 차이"], "difficulty": "중급"}},
        {{"day": 6, "topic": "이번 주 N3 문법 종합 복습", "focus": ["조건/추측 표현 총정리", "혼동하기 쉬운 표현 구별"], "difficulty": "복습"}},
        {{"day": 7, "topic": "N3 문법 실전 문제 풀이", "focus": ["JLPT 기출 유형 문제", "문맥 파악 연습"], "difficulty": "복습"}}
    ]
}}

═══════════════════════════════════════════════════════════
☁️ 예시 4 - AWS 자격증 주간 (weekly_title: "AWS EC2와 네트워킹 기초")
═══════════════════════════════════════════════════════════
{{
    "daily_curriculum": [
        {{"day": 1, "topic": "EC2 인스턴스 기본 개념", "focus": ["인스턴스 타입", "AMI 개념", "키 페어와 보안 그룹"], "difficulty": "기초"}},
        {{"day": 2, "topic": "EC2 인스턴스 생성 및 연결", "focus": ["인스턴스 생성 과정", "SSH 접속", "인스턴스 상태 관리"], "difficulty": "기초"}},
        {{"day": 3, "topic": "VPC 기초: 서브넷과 라우팅", "focus": ["VPC 개념", "퍼블릭/프라이빗 서브넷", "라우팅 테이블"], "difficulty": "중급"}},
        {{"day": 4, "topic": "보안 그룹과 NACL", "focus": ["인바운드/아웃바운드 규칙", "상태 저장 vs 비저장", "보안 모범 사례"], "difficulty": "중급"}},
        {{"day": 5, "topic": "ELB와 Auto Scaling 기초", "focus": ["로드 밸런서 종류", "Auto Scaling 그룹", "고가용성 아키텍처"], "difficulty": "중급"}},
        {{"day": 6, "topic": "이번 주 EC2/네트워킹 복습", "focus": ["핵심 개념 정리", "자주 출제되는 포인트"], "difficulty": "복습"}},
        {{"day": 7, "topic": "AWS 자격증 실전 문제 풀이", "focus": ["EC2/VPC 관련 기출 유형", "시나리오 문제 연습"], "difficulty": "복습"}}
    ]
}}
</topic_specific_examples>

<output_format>
정확히 7일치의 커리큘럼을 생성하세요.

{{
    "daily_curriculum": [
        {{
            "day": 1,
            "topic": "오늘 배울 구체적인 학습 주제 (20-50자)",
            "focus": ["핵심 학습 포인트 1", "핵심 학습 포인트 2", "핵심 학습 포인트 3"],
            "difficulty": "기초" | "중급" | "심화" | "복습"
        }},
        // ... day 2 ~ day 7 ...
    ]
}}
</output_format>

<thinking>
응답 전 확인:
1. 7일 모두 주간 학습 주제({weekly_title}) 범위 내인가?
2. 주간 목표에 없는 다른 영역을 포함하지 않았는가?
3. 각 일자의 topic이 충분히 구체적인가?
4. 점진적 심화 구조를 따르고 있는가?
</thinking>

JSON만 응답하세요."""


# ============================================================================
# Phase 2: 문제 생성
# ============================================================================
LEARNING_DAILY_QUESTIONS_PROMPT = """당신은 학습 효과를 극대화하는 문제 출제 전문가입니다.
오늘의 **구체적인 학습 내용**을 확인하는 문제를 출제합니다.

<context>
전체 학습 주제: {topic}
현재 위치: {month_number}개월차 {week_number}주차 {day_number}일차
학습 기간: {duration_months}개월
학습 강도: {intensity}
{interview_section}
</context>

<today_learning>
═══════════════════════════════════════════════════════════
📚 오늘의 학습 내용 (★★★ 문제는 이 내용에서만 출제하세요! ★★★)
═══════════════════════════════════════════════════════════
주간 학습 주제: {weekly_title}
주간 학습 설명: {weekly_description}

┌─────────────────────────────────────────────────────────┐
│ ★★★ 오늘 배울 내용 (이 내용에서만 출제!) ★★★             │
├─────────────────────────────────────────────────────────┤
│ 제목: {daily_topic}                                      │
│ 핵심 학습 포인트: {daily_focus}                           │
│ 난이도: {daily_difficulty}                               │
└─────────────────────────────────────────────────────────┘
</today_learning>

<critical_constraints>
═══════════════════════════════════════════════════════════
⚠️⚠️⚠️ 가장 중요한 규칙 - 절대 위반 금지 ⚠️⚠️⚠️
═══════════════════════════════════════════════════════════

1. 모든 문제는 <today_learning>의 "오늘 배울 내용"에서만 출제
   ✅ 오늘 주제: "{daily_topic}"
   ✅ 핵심 포인트: {daily_focus}
   → 이 내용을 벗어난 문제는 절대 금지!

2. ❌ 절대 출제하면 안 되는 문제 유형:
   - 오늘 학습 범위를 벗어난 내용
   - 주간 학습 목표({weekly_title})에 없는 다른 영역
   - 아직 배우지 않은 심화 내용
   - 문제에서 오늘 주제({daily_topic})와 관련 없는 개념

   ❌ 구체적 금지 예시:
   - "토익 문법" 주간인데 LC 듣기 관련 문제 출제
   - "8품사" 학습일인데 "관계대명사" 문제 출제
   - "Python 변수" 학습일인데 "함수" 문제 출제
   - "일본어 조건문" 학습일인데 "경어" 문제 출제

3. 문제에 오늘 학습 내용을 직접 반영:
   ❌ 나쁜 예: "다음 중 올바른 것은?" (모호함)
   ✅ 좋은 예: "{daily_topic}에서 배운 OOO에 관한 문제입니다"

4. 난이도 범위 준수:
   - 오늘 난이도가 "{daily_difficulty}"입니다
   - "기초"면 심화 문제 출제 X
   - "복습"이면 이번 주 전체 범위에서 출제 가능
</critical_constraints>

<intensity_rules>
학습 강도별 문제 수 (엄수 필수):
- light: 정확히 6개
- moderate: 정확히 10개
- intense: 정확히 15개

현재 강도 "{intensity}"에 따라 정확히 {question_count}개 생성하세요.
</intensity_rules>

<question_requirements>
1. 문제 개수: 정확히 {question_count}개

2. 문제 유형 배분:
   - ESSAY (서술형): 30% - 개념 이해도 확인
   - MULTIPLE_CHOICE (객관식): 40% - 핵심 개념 이해
   - SHORT_ANSWER (단답식): 30% - 용어/사실 확인

3. 문제 품질:
   - 오늘 학습 내용({daily_topic})과 직접 관련된 문제
   - 핵심 포인트({daily_focus})를 문제에 반영
   - 실제 시험/면접에서 출제될 수 있는 실용적 문제
   - 정답 해설에 학습 포인트 명시
</question_requirements>

<topic_specific_examples>
═══════════════════════════════════════════════════════════
📖 토익 문법 예시 (오늘 주제: "현재완료와 과거완료 비교")
═══════════════════════════════════════════════════════════
{{
    "question_type": "MULTIPLE_CHOICE",
    "question_text": "[현재완료 vs 과거완료] 다음 빈칸에 알맞은 시제는? 'The project _____ completed before the deadline yesterday.'",
    "choices": ["has been", "had been", "was being", "is being"],
    "correct_answer": "1",
    "hint": "'before the deadline yesterday'라는 과거의 기준점에 주목하세요. 어떤 시제가 '과거보다 더 과거'를 표현하나요?",
    "explanation": "과거의 특정 시점(yesterday의 deadline) 이전에 완료된 동작을 나타내므로 과거완료(had been)가 정답입니다. 현재완료(has been)는 과거부터 '현재까지' 연결될 때 사용합니다."
}}

{{
    "question_type": "SHORT_ANSWER",
    "question_text": "[현재완료 공식] 현재완료 시제를 만드는 공식을 쓰세요. (have/has + ?)",
    "correct_answer": "past participle (또는 p.p., 과거분사)",
    "hint": "동사의 3단 변화(원형-과거-?)에서 세 번째 형태입니다.",
    "explanation": "현재완료는 'have/has + 과거분사(past participle, p.p.)'로 구성됩니다. 예: have eaten, has gone, have been"
}}

{{
    "question_type": "ESSAY",
    "question_text": "[현재완료 vs 과거완료] 현재완료와 과거완료의 차이점을 '시간 기준점'의 관점에서 설명하고, 각각 예문을 1개씩 제시하세요.",
    "correct_answer": "현재완료(have/has + p.p.)는 과거의 동작이 현재까지 영향을 미칠 때 사용합니다. 기준점이 '현재'입니다. (예: I have lived here for 5 years - 5년 전부터 지금까지 살고 있음) 과거완료(had + p.p.)는 과거의 특정 시점 이전에 완료된 동작을 나타낼 때 사용합니다. 기준점이 '과거의 특정 시점'입니다. (예: I had finished the work before he arrived - 그가 도착하기 전에 이미 끝냄)",
    "hint": "각 시제의 '기준점'이 현재인지 과거인지 구분하세요. 그리고 예문에서 시간 관계를 명확히 하세요.",
    "explanation": "핵심 키워드: 기준점(현재 vs 과거), 영향/연속성(현재완료), 선행 완료(과거완료). 이 개념들이 포함되면 좋은 답변입니다."
}}

═══════════════════════════════════════════════════════════
💻 Python 예시 (오늘 주제: "리스트(list)와 튜플(tuple)")
═══════════════════════════════════════════════════════════
{{
    "question_type": "MULTIPLE_CHOICE",
    "question_text": "[리스트 vs 튜플] 다음 중 리스트와 튜플의 가장 핵심적인 차이점은?",
    "choices": ["리스트는 순서가 없고 튜플은 순서가 있다", "리스트는 수정 가능(mutable)하고 튜플은 수정 불가(immutable)하다", "리스트는 []로 생성하고 튜플은 {{}}로 생성한다", "튜플이 리스트보다 더 많은 내장 메서드를 가진다"],
    "correct_answer": "1",
    "hint": "데이터를 추가/삭제/변경할 수 있는지(mutability)를 생각해보세요.",
    "explanation": "리스트는 mutable(수정 가능)하여 append, remove 등으로 변경할 수 있고, 튜플은 immutable(수정 불가)하여 생성 후 변경이 불가합니다. 리스트는 [], 튜플은 ()로 생성합니다."
}}

{{
    "question_type": "SHORT_ANSWER",
    "question_text": "[리스트 슬라이싱] 리스트 my_list = [1, 2, 3, 4, 5]에서 인덱스 1부터 3까지의 요소를 가져오는 슬라이싱 코드를 작성하세요.",
    "correct_answer": "my_list[1:4]",
    "hint": "슬라이싱은 [시작:끝] 형태이며, 끝 인덱스는 포함되지 않습니다.",
    "explanation": "Python 슬라이싱에서 [1:4]는 인덱스 1, 2, 3의 요소를 반환합니다 (4는 미포함). 결과: [2, 3, 4]"
}}

{{
    "question_type": "ESSAY",
    "question_text": "[리스트 vs 튜플 활용] 리스트와 튜플을 각각 어떤 상황에서 사용하는 것이 적절한지 설명하고, 실제 코드 예시를 각각 1개씩 제시하세요.",
    "correct_answer": "리스트는 데이터가 변경될 가능성이 있을 때 사용합니다. 예: 장바구니 목록 cart = ['사과', '바나나']에서 cart.append('오렌지')로 추가 가능. 튜플은 데이터가 변경되면 안 되거나 고정된 값일 때 사용합니다. 예: 좌표 position = (10, 20)이나 RGB 색상 color = (255, 128, 0)처럼 의미 있는 순서가 있는 고정 데이터에 적합합니다.",
    "hint": "mutability(수정 가능 여부)가 핵심입니다. 실제 상황에서 데이터가 변경되어야 하는지 생각해보세요.",
    "explanation": "핵심: 리스트=동적 데이터, 튜플=고정 데이터. 딕셔너리 키로 튜플은 사용 가능하나 리스트는 불가능한 것도 중요한 차이입니다."
}}

═══════════════════════════════════════════════════════════
🇯🇵 일본어 예시 (오늘 주제: "조건 표현 〜ば, 〜たら, 〜なら")
═══════════════════════════════════════════════════════════
{{
    "question_type": "MULTIPLE_CHOICE",
    "question_text": "[조건 표현 선택] 다음 문장에서 가장 자연스러운 조건 표현은? '明日 雨が( )、試合は中止です。'",
    "choices": ["降れば", "降ったら", "降るなら", "降ると"],
    "correct_answer": "0",
    "hint": "가정적 조건(~하면)을 나타내는 표현을 선택하세요. 〜ば는 어떤 상황에서 주로 사용하나요?",
    "explanation": "〜ば는 일반적인 가정 조건을 나타냅니다. '비가 내리면'이라는 가정을 표현할 때 자연스럽습니다. 〜たら는 시간적 순서를, 〜なら는 상대방의 말을 받을 때 주로 사용합니다."
}}

{{
    "question_type": "SHORT_ANSWER",
    "question_text": "[〜ば 활용] 동사 '食べる(たべる)'를 〜ば형으로 활용하세요.",
    "correct_answer": "食べれば (たべれば)",
    "hint": "2그룹 동사(る 동사)의 ば형은 'る'를 'れば'로 바꿉니다.",
    "explanation": "食べる → 食べれば. 2그룹 동사는 어미 'る'를 'れば'로 바꿉니다. 1그룹 동사는 어미를 'え단 + ば'로 바꿉니다 (예: 行く → 行けば)."
}}

{{
    "question_type": "ESSAY",
    "question_text": "[〜ば, 〜たら, 〜なら 비교] 세 가지 조건 표현의 차이점을 설명하고, 각각 자연스러운 예문을 1개씩 제시하세요.",
    "correct_answer": "〜ば: 일반적인 가정 조건, 자연법칙이나 습관 (春になれば、桜が咲く - 봄이 되면 벚꽃이 핀다). 〜たら: 시간적 순서, 완료 후 상황, 개인적 상황 (家に帰ったら、電話してください - 집에 돌아가면 전화해주세요). 〜なら: 상대방의 말/상황을 받아서 조언/의견 제시 (日本に行くなら、京都がおすすめです - 일본에 간다면 교토를 추천합니다)",
    "hint": "각 표현이 주로 어떤 상황에서 사용되는지, 뉘앙스 차이를 떠올려보세요.",
    "explanation": "핵심 구별점: 〜ば(일반 가정, 법칙), 〜たら(시간적 순서, 완료 후), 〜なら(상대방 상황 받기, 조언). 문맥에 따라 자연스러운 표현이 다릅니다."
}}

═══════════════════════════════════════════════════════════
☁️ AWS 예시 (오늘 주제: "VPC 기초: 서브넷과 라우팅")
═══════════════════════════════════════════════════════════
{{
    "question_type": "MULTIPLE_CHOICE",
    "question_text": "[퍼블릭 서브넷 조건] AWS VPC에서 서브넷이 '퍼블릭 서브넷'이 되기 위한 필수 조건은?",
    "choices": ["NAT Gateway 연결", "인터넷 게이트웨이로 향하는 라우팅 규칙과 퍼블릭 IP", "보안 그룹에서 모든 인바운드 허용", "프라이빗 IP만 할당"],
    "correct_answer": "1",
    "hint": "퍼블릭 서브넷의 인스턴스가 인터넷과 직접 통신하려면 무엇이 필요한지 생각해보세요.",
    "explanation": "퍼블릭 서브넷은 인터넷 게이트웨이(IGW)로 향하는 라우팅 규칙이 있고, 인스턴스에 퍼블릭 IP가 할당되어야 합니다. NAT Gateway는 프라이빗 서브넷에서 아웃바운드 인터넷 접근에 사용됩니다."
}}

{{
    "question_type": "SHORT_ANSWER",
    "question_text": "[라우팅 대상] 라우팅 테이블에서 '0.0.0.0/0'은 무엇을 의미하나요?",
    "correct_answer": "모든 IP 주소 (또는 기본 라우트, default route)",
    "hint": "0.0.0.0/0의 CIDR 범위를 생각해보세요. /0은 모든 비트가 와일드카드입니다.",
    "explanation": "0.0.0.0/0은 모든 IP 주소를 의미하며, 다른 규칙에 매칭되지 않는 모든 트래픽의 기본 경로(default route)로 사용됩니다."
}}
</topic_specific_examples>

<output_format>
정확히 {question_count}개의 문제를 포함해야 합니다!

{{
    "questions": [
        {{
            "question_type": "MULTIPLE_CHOICE" | "ESSAY" | "SHORT_ANSWER",
            "question_text": "[{daily_topic} 관련] 구체적인 문제 내용",
            "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],  // 객관식만 (4지선다 필수)
            "correct_answer": "정답 (객관식: 0-based 인덱스 문자열)",
            "hint": "오늘 학습 내용과 연결된 구체적인 힌트",
            "explanation": "왜 이것이 정답인지 + 학습 포인트"
        }}
    ]
}}
</output_format>

<final_check>
✅ 출제 전 최종 체크리스트:
1. [ ] 모든 문제가 오늘 주제 "{daily_topic}"에서만 출제되었는가?
2. [ ] 주간 목표({weekly_title}) 범위를 벗어나지 않았는가?
3. [ ] 핵심 학습 포인트({daily_focus})가 문제에 반영되었는가?
4. [ ] 오늘 난이도({daily_difficulty})에 맞는 수준인가?
5. [ ] 정확히 {question_count}개의 문제가 있는가?

위 항목 중 하나라도 NO이면 다시 작성하세요!
</final_check>

JSON만 응답하세요."""


GRADING_PROMPT = """당신은 공정하고 건설적인 피드백을 제공하는 채점 전문가입니다.
학습자의 답변을 채점하고 맞춤형 피드백을 제공합니다.

<question_info>
문제 유형: {question_type}
문제: {question_text}
정답: {correct_answer}
해설: {explanation}
</question_info>

<student_answer>
{user_answer}
</student_answer>

<grading_rules>
1. 객관식 (MULTIPLE_CHOICE):
   - 정답 인덱스와 정확히 일치하면 is_correct = true
   - score = null (사용하지 않음)

2. 단답식 (SHORT_ANSWER):
   - 핵심 단어/개념이 일치하면 is_correct = true
   - 대소문자, 띄어쓰기는 유연하게 처리
   - 동의어나 약어도 정답으로 인정
   - score = null (사용하지 않음)

3. 서술형 (ESSAY):
   - is_correct = true/false (핵심 개념 50% 이상 포함 시 true)
   - score = 0~100 (핵심 개념 포함도, 논리적 구성, 정확성)
   - 채점 기준:
     * 핵심 개념 포함 (50%)
     * 논리적 설명 (30%)
     * 정확한 용어 사용 (20%)
</grading_rules>

<feedback_principles>
1. 긍정적인 부분을 먼저 언급
2. 틀린 부분은 왜 틀렸는지 명확히 설명
3. 학습 동기 유지를 위한 격려 포함
4. 추가 학습이 필요한 부분 제안
</feedback_principles>

<output_format>
{{
    "is_correct": true | false,
    "score": 0-100 | null,
    "feedback": "개인화된 피드백 (2-4문장, 격려와 개선점 포함)",
    "key_points_matched": ["맞춘 핵심 포인트"],
    "key_points_missed": ["놓친 핵심 포인트"]
}}
</output_format>

JSON만 응답하세요."""


DAILY_FEEDBACK_PROMPT = """당신은 따뜻하고 전문적인 학습 코치입니다.
오늘 학습 결과를 분석하여 맞춤형 피드백을 제공합니다.

<today_result>
학습 주제: {topic}
{month_number}개월차 {week_number}주차 {day_number}일차

총 문제 수: {total_questions}
맞은 문제: {correct_count}
정답률: {accuracy_rate}%
합격 기준: 70%

문제별 결과:
{questions_summary}
</today_result>

<feedback_guidelines>
1. 전체 학습 평가 (2-3문장):
   - 정답률에 따른 전반적인 평가
   - 오늘 학습의 핵심 달성도

2. 잘한 점 (2개):
   - 구체적으로 어떤 부분을 잘 이해했는지
   - 특히 잘 푼 문제 유형 언급

3. 개선점 (2개):
   - 어떤 개념을 더 학습해야 하는지
   - 구체적인 학습 방향 제시

4. 내일 학습 조언:
   - 오늘 결과를 바탕으로 내일 집중할 부분
</feedback_guidelines>

<tone>
- 정답률 80% 이상: 축하와 격려 위주
- 정답률 70-79%: 성취 인정 + 보완점 제시
- 정답률 70% 미만: 격려 위주 + 구체적 학습 조언
</tone>

<output_format>
{{
    "summary": "오늘 학습 종합 평가 (2-3문장)",
    "strengths": ["잘한 점 1", "잘한 점 2"],
    "improvements": ["개선점 1", "개선점 2"],
    "tomorrow_focus": "내일 집중해야 할 부분"
}}
</output_format>

JSON만 응답하세요."""


REVIEW_QUESTIONS_PROMPT = """당신은 효과적인 복습을 설계하는 학습 전문가입니다.
틀린 문제들을 분석하여 복습용 변형 문제를 생성합니다.

<wrong_questions>
{wrong_questions_list}
</wrong_questions>

<review_principles>
1. 각 틀린 문제에 대해 1-2개의 변형 문제 생성
2. 같은 개념을 다른 각도에서 확인
3. 난이도는 원래 문제와 유사하거나 약간 쉽게
4. 학습자가 개념을 완전히 이해했는지 재확인
</review_principles>

<variation_strategies>
- 같은 개념, 다른 예시 사용
- 질문 형식 변경 (객관식 → 단답식 등)
- 관련 개념으로 확장
- 실제 적용 시나리오 제시
</variation_strategies>

<output_format>
{{
    "review_questions": [
        {{
            "original_question_id": "원본 문제 ID",
            "question_type": "MULTIPLE_CHOICE" | "ESSAY" | "SHORT_ANSWER",
            "question_text": "변형 문제 내용",
            "choices": ["선택지1", ...],  // 객관식만
            "correct_answer": "정답",
            "hint": "힌트",
            "explanation": "해설",
            "review_focus": "이 문제가 확인하는 핵심 개념"
        }}
    ]
}}
</output_format>

JSON만 응답하세요."""


def build_questions_summary(question_results: list) -> str:
    """문제별 결과를 요약 문자열로 변환"""
    lines = []
    for i, result in enumerate(question_results, 1):
        status = "O" if result.get("is_correct") else "X"
        q_type = result.get("question_type", "UNKNOWN")
        lines.append(f"{i}. [{status}] {q_type}: {result.get('question_text', '')[:50]}...")
    return "\n".join(lines)


def build_wrong_questions_list(wrong_questions: list) -> str:
    """틀린 문제 목록을 프롬프트용 문자열로 변환"""
    lines = []
    for i, wq in enumerate(wrong_questions, 1):
        lines.append(f"""
문제 {i}:
- ID: {wq.get('question_id')}
- 유형: {wq.get('question_type')}
- 문제: {wq.get('question_text')}
- 정답: {wq.get('correct_answer')}
- 학생 답변: {wq.get('user_answer')}
- 해설: {wq.get('explanation')}
""")
    return "\n".join(lines)


# Intensity configuration
INTENSITY_CONFIG = {
    "light": 6,      # 가벼운 학습: 6문제
    "moderate": 10,  # 보통 학습: 10문제
    "intense": 15,   # 집중 학습: 15문제
}


def calculate_intensity(topic: str, duration_months: int) -> tuple[str, int]:
    """학습 주제와 기간을 기반으로 학습 강도를 계산합니다.

    규칙:
    - 어려운 주제 + 짧은 기간 = intense (15문제)
    - 보통 주제 + 보통 기간 = moderate (10문제)
    - 쉬운 주제 + 긴 기간 = light (6문제)

    Returns:
        tuple[str, int]: (intensity 이름, 문제 수)
    """
    topic_lower = topic.lower()

    # 어려운 주제 키워드 (시험, 자격증, 고급 등)
    hard_keywords = [
        "토익", "toeic", "토플", "toefl", "ielts", "jlpt", "n1", "n2",
        "정보처리기사", "aws", "자격증", "certificate",
        "알고리즘", "algorithm", "코딩테스트", "coding test",
        "advanced", "고급", "심화", "professional", "expert",
        "900", "800", "990", "만점",
    ]

    # 기초 주제 키워드
    easy_keywords = [
        "입문", "기초", "beginner", "basic", "introduction", "intro",
        "처음", "시작", "first", "getting started", "초보",
    ]

    # 주제 난이도 점수 (-1: 쉬움, 0: 보통, 1: 어려움)
    topic_difficulty = 0
    for keyword in hard_keywords:
        if keyword in topic_lower:
            topic_difficulty = 1
            break
    if topic_difficulty == 0:
        for keyword in easy_keywords:
            if keyword in topic_lower:
                topic_difficulty = -1
                break

    # 기간 기반 점수 (짧을수록 높음)
    if duration_months <= 1:
        duration_pressure = 2  # 매우 빡빡
    elif duration_months <= 2:
        duration_pressure = 1  # 빡빡
    elif duration_months <= 3:
        duration_pressure = 0  # 보통
    else:
        duration_pressure = -1  # 여유로움

    # 종합 점수 계산
    total_score = topic_difficulty + duration_pressure

    if total_score >= 2:
        intensity = "intense"
    elif total_score >= 0:
        intensity = "moderate"
    else:
        intensity = "light"

    return intensity, INTENSITY_CONFIG[intensity]


def get_weekend_intensity(base_intensity: str) -> tuple[str, int]:
    """주말(복습일)용 문제 수를 반환합니다. 기본 강도보다 한 단계 낮음."""
    intensity_order = ["light", "moderate", "intense"]
    current_index = intensity_order.index(base_intensity)
    weekend_index = max(0, current_index - 1)
    weekend_intensity = intensity_order[weekend_index]
    return weekend_intensity, INTENSITY_CONFIG[weekend_intensity]


# ============================================================================
# Helper Functions for 2-Stage Generation (NEW)
# ============================================================================
def format_daily_focus(focus_list: list) -> str:
    """학습 포인트 리스트를 문자열로 포맷팅합니다.

    Args:
        focus_list: 핵심 학습 포인트 리스트

    Returns:
        쉼표로 구분된 문자열
    """
    if not focus_list:
        return "해당 없음"
    return ", ".join(focus_list)


def get_difficulty_korean(difficulty: str) -> str:
    """난이도를 한글로 변환합니다.

    Args:
        difficulty: 영문 또는 한글 난이도

    Returns:
        한글 난이도 문자열
    """
    mapping = {
        "기초": "기초",
        "중급": "중급",
        "심화": "심화",
        "복습": "복습",
        "basic": "기초",
        "intermediate": "중급",
        "advanced": "심화",
        "review": "복습",
    }
    return mapping.get(difficulty, "기초")


def validate_curriculum(curriculum: list, weekly_title: str) -> bool:
    """생성된 커리큘럼이 유효한지 검증합니다.

    Args:
        curriculum: 7일간의 커리큘럼 리스트
        weekly_title: 주간 학습 제목

    Returns:
        유효하면 True, 아니면 False
    """
    if not curriculum or len(curriculum) != 7:
        return False

    for day in curriculum:
        if not day.get("topic") or not day.get("focus"):
            return False
        if day.get("day") not in range(1, 8):
            return False

    return True
