"""Feedback prompts for roadmap refinement chat."""
import json
from typing import List, Optional


FEEDBACK_ANALYSIS_PROMPT = """당신은 학습 로드맵 개선 전문가입니다.
사용자의 피드백을 분석하고 로드맵을 적절히 수정합니다.

<current_roadmap>
{roadmap_json}
</current_roadmap>

{interview_section}

<chat_history>
{recent_messages}
</chat_history>

<user_feedback>
{user_message}
</user_feedback>

<rules>
1. 피드백 분석: 사용자가 원하는 변경 사항을 정확히 파악하세요
2. 수정 범위 결정:
   - "none": 칭찬, 만족 표현, 또는 질문만 있는 경우
   - "weekly": 특정 주간 과제만 수정이 필요한 경우
   - "monthly": 월간 목표 수정이 필요한 경우 (관련 주간도 함께 수정)
   - "both": 여러 월에 걸쳐 대대적인 수정이 필요한 경우
3. 수정 원칙:
   - 최소한의 변경으로 요구사항 반영
   - monthly 수정 시 해당 월의 weekly도 일관성 있게 조정
   - 기존 구조와 난이도 흐름 유지
4. 응답 스타일:
   - 친근하고 격려하는 톤
   - 어떤 변경을 했는지 명확히 설명
   - 추가 질문이 있으면 물어보기
</rules>

<output_format>
{{
    "response": "사용자에게 전달할 친근한 메시지 (변경 내용 설명 포함, 한국어)",
    "modification_type": "none" | "weekly" | "monthly" | "both",
    "modifications": {{
        "monthly_goals": [
            // 수정된 월 목표만 포함 (month_number로 식별)
            // 예: {{"month_number": 1, "title": "새 제목", "description": "새 설명"}}
        ],
        "weekly_tasks": [
            // 수정된 주간 과제만 포함
            // 예: {{"month_number": 1, "week_number": 2, "title": "새 제목", "description": "새 설명"}}
        ]
    }}
}}
</output_format>

<important>
- 피드백이 칭찬, 감사, 만족 표현이면 modification_type을 "none"으로 설정
- modifications의 배열이 비어있으면 빈 배열 [] 반환
- JSON만 응답하세요 (마크다운 코드 블록 없이)
</important>"""


WELCOME_MESSAGE = """안녕하세요! 로드맵이 생성되었어요.

지금부터 로드맵을 함께 다듬어볼까요? 예를 들어:
- "1월차가 너무 어려워요"
- "2주차 내용이 이해가 안 돼요"
- "전체적으로 더 실습 위주로 해주세요"

마음에 드시면 '확정' 버튼을 눌러주세요!"""


def format_roadmap_compact(roadmap_data: dict) -> str:
    """컴팩트한 로드맵 JSON 생성 (토큰 절약)."""
    compact = {
        "title": roadmap_data.get("title", ""),
        "topic": roadmap_data.get("topic", ""),
        "duration": roadmap_data.get("duration_months", 0),
        "months": []
    }

    monthly_goals = roadmap_data.get("monthly_goals", [])
    weekly_tasks = roadmap_data.get("weekly_tasks", [])

    for goal in monthly_goals:
        month_num = goal.get("month_number")
        month_data = {
            "m": month_num,
            "title": goal.get("title", ""),
            "desc": goal.get("description", "")[:100],  # 설명 축약
            "weeks": []
        }

        # 해당 월의 주간 과제 찾기
        for wt in weekly_tasks:
            if wt.get("month_number") == month_num:
                weeks = wt.get("weeks", [])
                for w in weeks:
                    month_data["weeks"].append({
                        "w": w.get("week_number"),
                        "title": w.get("title", ""),
                        "desc": w.get("description", "")[:80]
                    })
                break

        compact["months"].append(month_data)

    return json.dumps(compact, ensure_ascii=False, indent=2)


def format_recent_messages(messages: List[dict], limit: int = 5) -> str:
    """최근 메시지 포맷팅."""
    if not messages:
        return "(첫 대화입니다)"

    recent = messages[-(limit * 2):]  # 최근 N개 대화
    formatted = []

    for msg in recent:
        role = "사용자" if msg.get("role") == "user" else "AI"
        content = msg.get("content", "")[:200]  # 메시지 축약
        formatted.append(f"{role}: {content}")

    return "\n".join(formatted)


def build_interview_section(interview_context: Optional[dict]) -> str:
    """인터뷰 컨텍스트 섹션 생성."""
    if not interview_context:
        return ""

    return f"""<user_profile>
학습자 정보:
- 구체적 목표: {interview_context.get('specific_goal', '미정')}
- 현재 수준: {interview_context.get('current_level', '미정')}
- 가용 시간: {interview_context.get('available_resources', {}).get('daily_hours', '미정')}시간/일
- 동기: {interview_context.get('motivation', '미정')}
- 예상 어려움: {', '.join(interview_context.get('challenges', []))}
</user_profile>"""
