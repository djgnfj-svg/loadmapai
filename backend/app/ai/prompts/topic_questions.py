"""주제별 SMART 질문 템플릿.

주제 카테고리에 따라 맞춤형 질문 예시를 제공하여
더 구체적이고 관련성 높은 질문을 생성할 수 있도록 합니다.
"""

from typing import Dict, List


# ============ 주제 카테고리별 SMART 질문 템플릿 ============

TOPIC_QUESTION_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "programming": {
        "specific": [
            "어떤 종류의 프로젝트를 만들어보고 싶으세요? (웹앱/모바일앱/데이터 분석 등)",
            "배우고 싶은 언어나 프레임워크가 있으세요?",
            "만들고 싶은 구체적인 서비스나 기능이 있나요?",
        ],
        "measurable": [
            "포트폴리오에 몇 개의 프로젝트를 완성하고 싶으세요?",
            "취업/이직이 목표라면, 목표 회사 규모나 분야는?",
            "달성하고 싶은 구체적인 기술 스택이 있나요?",
        ],
        "achievable": [
            "현재 코딩 경험이 어느 정도 되시나요?",
            "이전에 프로그래밍을 시도해 본 적이 있나요?",
            "컴퓨터 관련 전공이신가요, 비전공자이신가요?",
        ],
        "relevant": [
            "프로그래밍을 배워서 하고 싶은 것이 무엇인가요?",
            "현재 직업과 연관이 있나요?",
        ],
        "time_bound": [
            "취업이나 이직 목표 시기가 있나요?",
            "특정 프로젝트 마감일이 있나요?",
        ],
    },
    "language": {
        "specific": [
            "어떤 상황에서 사용하고 싶으세요? (여행/업무/시험/취미)",
            "목표하는 레벨이 있나요? (회화 수준, 원서 읽기 등)",
            "특별히 집중하고 싶은 영역이 있나요? (말하기/듣기/읽기/쓰기)",
        ],
        "measurable": [
            "목표 점수나 레벨이 있나요? (TOEIC, JLPT 등)",
            "원어민과 대화가 가능한 수준을 원하시나요?",
            "특정 자격증 취득이 목표인가요?",
        ],
        "achievable": [
            "현재 수준을 스스로 평가한다면? (초급/중급/고급)",
            "이전에 언어 학습 경험이 있으신가요?",
            "외국어 학습에 자신 있는 편인가요?",
        ],
        "relevant": [
            "왜 이 언어를 배우고 싶으세요?",
            "업무나 학업에 필요한가요?",
        ],
        "time_bound": [
            "시험 일정이 정해져 있나요?",
            "해외 여행/출장 계획이 있나요?",
        ],
    },
    "certification": {
        "specific": [
            "목표하는 자격증 이름이 있으세요?",
            "이 자격증으로 무엇을 하고 싶으세요?",
            "관련 분야에서 어떤 역할을 하고 싶으세요?",
        ],
        "measurable": [
            "목표 점수나 등급이 있나요?",
            "합격만 하면 되나요, 아니면 높은 점수가 필요한가요?",
        ],
        "achievable": [
            "관련 분야 경험이나 배경지식이 있나요?",
            "이전에 비슷한 시험을 본 적이 있나요?",
            "현재 관련 업무를 하고 계신가요?",
        ],
        "relevant": [
            "이 자격증이 왜 필요하세요?",
            "취업이나 승진에 필요한가요?",
        ],
        "time_bound": [
            "시험 일정이 정해져 있나요?",
            "언제까지 취득해야 하나요?",
        ],
    },
    "fitness": {
        "specific": [
            "구체적인 목표가 있나요? (체중 감량/근력 향상/체력 증진)",
            "어떤 운동을 해보고 싶으세요?",
            "운동 목적이 건강인가요, 미적인 목표인가요?",
        ],
        "measurable": [
            "목표 체중이나 체지방률이 있나요?",
            "달리기 기록이나 역기 중량 목표가 있나요?",
        ],
        "achievable": [
            "현재 운동을 하고 계신가요?",
            "과거에 운동을 해본 경험이 있나요?",
            "부상이나 건강 문제가 있나요?",
        ],
        "relevant": [
            "왜 운동을 시작하려고 하세요?",
            "특별한 계기가 있나요?",
        ],
        "time_bound": [
            "특별한 이벤트가 있나요? (결혼식, 여름 휴가 등)",
            "목표 달성 기한이 있나요?",
        ],
    },
    "music": {
        "specific": [
            "어떤 악기를 배우고 싶으세요?",
            "연주하고 싶은 곡이나 장르가 있나요?",
            "밴드 활동이나 개인 연주 중 어떤 것을 원하세요?",
        ],
        "measurable": [
            "어느 정도 수준까지 연주하고 싶으세요?",
            "특정 곡을 완주하는 것이 목표인가요?",
        ],
        "achievable": [
            "악기 연주 경험이 있으신가요?",
            "악보를 읽을 수 있나요?",
            "악기가 있으신가요?",
        ],
        "relevant": [
            "왜 이 악기를 배우고 싶으세요?",
            "취미인가요, 전문적으로 하고 싶으신가요?",
        ],
        "time_bound": [
            "공연이나 발표회 계획이 있나요?",
        ],
    },
    "business": {
        "specific": [
            "어떤 사업 아이디어가 있으세요?",
            "목표 고객층은 누구인가요?",
            "어떤 문제를 해결하고 싶으세요?",
        ],
        "measurable": [
            "목표 매출이나 고객 수가 있나요?",
            "언제까지 런칭하고 싶으세요?",
        ],
        "achievable": [
            "관련 분야 경험이 있으신가요?",
            "창업 자금은 어느 정도 준비되어 있나요?",
            "현재 직장을 다니면서 준비하시나요?",
        ],
        "relevant": [
            "왜 창업을 하고 싶으세요?",
            "이 분야를 선택한 이유는?",
        ],
        "time_bound": [
            "사업 시작 목표 시기가 있나요?",
            "투자 유치 계획이 있나요?",
        ],
    },
    "general": {
        "specific": [
            "구체적으로 어떤 것을 배우고 싶으세요?",
            "이 분야에서 어떤 성과를 내고 싶으세요?",
        ],
        "measurable": [
            "목표 달성을 어떻게 확인하실 건가요?",
            "구체적인 목표 수치가 있나요?",
        ],
        "achievable": [
            "현재 이 분야에 대한 경험이 있으세요?",
            "이전에 비슷한 것을 시도해 본 적이 있나요?",
        ],
        "relevant": [
            "왜 이것을 배우고 싶으세요?",
        ],
        "time_bound": [
            "특별히 맞춰야 하는 일정이 있나요?",
        ],
    },
}

# ============ 주제 분류 키워드 ============

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "programming": [
        "python", "파이썬", "java", "자바", "javascript", "자바스크립트",
        "웹", "앱", "프로그래밍", "개발", "코딩", "프론트엔드", "백엔드",
        "react", "vue", "django", "spring", "flutter", "ios", "android",
        "데이터", "ai", "머신러닝", "딥러닝", "알고리즘", "코테", "코딩테스트",
    ],
    "language": [
        "영어", "english", "일본어", "japanese", "중국어", "chinese",
        "언어", "토익", "toeic", "토플", "toefl", "회화", "speaking",
        "jlpt", "hsk", "ielts", "듣기", "말하기", "작문",
        "스페인어", "프랑스어", "독일어", "한국어",
    ],
    "certification": [
        "자격증", "시험", "정보처리", "기사", "산업기사",
        "aws", "인증", "certificate", "정보보안", "네트워크",
        "빅데이터", "클라우드", "pmp", "cpa", "세무사", "회계사",
        "공인", "국가자격", "민간자격",
    ],
    "fitness": [
        "운동", "헬스", "gym", "다이어트", "체중", "근육",
        "요가", "필라테스", "러닝", "마라톤", "수영",
        "홈트", "pt", "크로스핏", "체력", "건강",
    ],
    "music": [
        "기타", "피아노", "드럼", "베이스", "바이올린",
        "악기", "음악", "작곡", "편곡", "보컬", "노래",
        "밴드", "재즈", "클래식", "팝", "rock",
    ],
    "business": [
        "창업", "사업", "스타트업", "startup", "마케팅",
        "경영", "기획", "투자", "매출", "브랜딩",
        "사이드프로젝트", "부업", "프리랜서",
    ],
}


def get_topic_category(topic: str) -> str:
    """주제를 카테고리로 분류합니다.

    Args:
        topic: 사용자가 입력한 주제

    Returns:
        카테고리 문자열 (programming, language, certification, fitness, music, business, general)
    """
    topic_lower = topic.lower()

    # 각 카테고리의 키워드와 매칭
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in topic_lower for keyword in keywords):
            return category

    return "general"


def get_topic_examples(topic: str) -> str:
    """주제에 맞는 SMART 질문 예시를 반환합니다.

    Args:
        topic: 사용자가 입력한 주제

    Returns:
        주제별 질문 예시 문자열
    """
    category = get_topic_category(topic)
    templates = TOPIC_QUESTION_TEMPLATES.get(category, TOPIC_QUESTION_TEMPLATES["general"])

    examples = []
    smart_labels = {
        "specific": "S (구체적 목표)",
        "measurable": "M (측정 가능)",
        "achievable": "A (달성 가능)",
        "relevant": "R (연관성)",
        "time_bound": "T (시간 제한)",
    }

    for smart_element, questions in templates.items():
        label = smart_labels.get(smart_element, smart_element)
        # 각 요소에서 첫 번째 질문만 선택
        if questions:
            examples.append(f"- [{label}] {questions[0]}")

    if examples:
        return "\n".join(examples)

    return "주제에 맞는 구체적인 질문을 생성하세요."


def get_all_template_questions(topic: str) -> Dict[str, List[str]]:
    """주제 카테고리의 모든 템플릿 질문을 반환합니다.

    Args:
        topic: 사용자가 입력한 주제

    Returns:
        SMART 요소별 질문 리스트 딕셔너리
    """
    category = get_topic_category(topic)
    return TOPIC_QUESTION_TEMPLATES.get(category, TOPIC_QUESTION_TEMPLATES["general"])
