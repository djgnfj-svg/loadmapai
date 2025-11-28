"""
AI-based roadmap editing workflow using LangGraph.

This module provides conversational editing of roadmaps through AI.
Users can request changes like:
- "D3 태스크를 좀 더 쉽게 바꿔줘"
- "1주차에 복습 시간 추가해줘"
- "난이도 낮춰줘"
"""

import json
from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class EditIntent(str, Enum):
    MODIFY = "modify"  # 수정
    ADD = "add"  # 추가
    DELETE = "delete"  # 삭제
    EXPLAIN = "explain"  # 설명 요청


class TargetType(str, Enum):
    ROADMAP = "roadmap"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


class EditChange(TypedDict):
    """단일 변경 항목"""
    id: str  # 변경 ID (적용 시 참조용)
    target_type: str  # roadmap/monthly/weekly/daily
    target_id: Optional[str]  # 기존 항목 ID (수정/삭제 시)
    action: str  # modify/add/delete
    field: Optional[str]  # 변경할 필드 (title, description 등)
    old_value: Optional[str]
    new_value: Optional[str]
    parent_id: Optional[str]  # 추가 시 부모 ID


class EditState(TypedDict):
    """AI 편집 워크플로우 상태"""
    # Input
    user_message: str
    roadmap_id: str
    roadmap_context: Dict[str, Any]  # 현재 로드맵 구조

    # Analysis
    intent: Optional[str]  # EditIntent
    targets: List[Dict[str, Any]]  # 대상 항목들

    # Output
    changes: List[EditChange]
    response_message: str
    suggestions: List[str]  # 추가 제안사항


def create_llm():
    """Create Claude LLM instance."""
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


INTENT_ANALYSIS_PROMPT = """당신은 학습 로드맵 편집을 돕는 AI 어시스턴트입니다.
사용자의 요청을 분석하여 의도와 대상을 파악해주세요.

현재 로드맵 구조:
{roadmap_context}

사용자 요청: {user_message}

분석할 내용:
1. 의도 (intent): modify(수정), add(추가), delete(삭제), explain(설명 요청) 중 하나
2. 대상 타입 (target_type): roadmap, monthly, weekly, daily 중 하나 또는 여러 개
3. 대상 식별: 어떤 항목을 수정/추가/삭제하려는지

응답 형식 (JSON):
{{
    "intent": "modify",
    "targets": [
        {{
            "target_type": "daily",
            "identifier": "D3" 또는 "월1주2일3" 또는 특정 ID,
            "description": "어떤 항목인지 설명"
        }}
    ],
    "understanding": "사용자 요청에 대한 이해를 한 문장으로"
}}

JSON만 응답하세요."""


GENERATE_CHANGES_PROMPT = """당신은 학습 로드맵 편집을 돕는 AI 어시스턴트입니다.
사용자의 요청에 따라 구체적인 변경사항을 생성해주세요.

현재 로드맵:
{roadmap_context}

사용자 요청: {user_message}
분석된 의도: {intent}
분석된 대상: {targets}

변경사항 생성 규칙:
1. 각 변경은 구체적이고 실행 가능해야 함
2. 기존 내용의 맥락을 유지하면서 개선
3. 하루 학습 시간({daily_available_minutes}분)을 고려
4. 학습 강도({intensity})를 고려

응답 형식 (JSON):
{{
    "changes": [
        {{
            "id": "change_1",
            "target_type": "daily",
            "target_id": "대상 UUID" 또는 null,
            "action": "modify",
            "field": "title" 또는 "description",
            "old_value": "기존 값",
            "new_value": "새 값",
            "parent_id": null
        }}
    ],
    "response_message": "사용자에게 보여줄 변경 설명 (친근한 톤)",
    "suggestions": ["추가 제안1", "추가 제안2"]
}}

JSON만 응답하세요."""


def format_roadmap_context(roadmap_data: Dict[str, Any]) -> str:
    """Format roadmap data for prompt context."""
    lines = []
    lines.append(f"로드맵: {roadmap_data.get('title', 'N/A')}")
    lines.append(f"주제: {roadmap_data.get('topic', 'N/A')}")
    lines.append(f"기간: {roadmap_data.get('duration_months', 'N/A')}개월")
    lines.append(f"하루 학습 시간: {roadmap_data.get('daily_available_minutes', 60)}분")
    lines.append(f"학습 강도: {roadmap_data.get('intensity', 'moderate')}")
    lines.append("")

    for monthly in roadmap_data.get("monthly_goals", []):
        lines.append(f"[M{monthly.get('month_number', '?')}] {monthly.get('title', 'N/A')}")

        for weekly in monthly.get("weekly_tasks", []):
            lines.append(f"  [W{weekly.get('week_number', '?')}] {weekly.get('title', 'N/A')}")

            for daily in weekly.get("daily_tasks", []):
                day = daily.get("day_number", "?")
                order = daily.get("order", 0)
                title = daily.get("title", "N/A")
                task_id = daily.get("id", "")
                if order > 0:
                    lines.append(f"    [D{day}.{order}] {title} (id: {task_id})")
                else:
                    lines.append(f"    [D{day}] {title} (id: {task_id})")

    return "\n".join(lines)


async def analyze_intent(
    user_message: str,
    roadmap_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Analyze user intent and identify targets."""
    llm = create_llm()
    formatted_context = format_roadmap_context(roadmap_context)

    prompt = INTENT_ANALYSIS_PROMPT.format(
        roadmap_context=formatted_context,
        user_message=user_message,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        return result
    except (json.JSONDecodeError, Exception) as e:
        return {
            "intent": "explain",
            "targets": [],
            "understanding": f"요청을 이해하지 못했습니다: {str(e)}",
        }


async def generate_changes(
    user_message: str,
    roadmap_context: Dict[str, Any],
    intent: str,
    targets: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate specific changes based on intent and targets."""
    llm = create_llm()
    formatted_context = format_roadmap_context(roadmap_context)

    prompt = GENERATE_CHANGES_PROMPT.format(
        roadmap_context=formatted_context,
        user_message=user_message,
        intent=intent,
        targets=json.dumps(targets, ensure_ascii=False),
        daily_available_minutes=roadmap_context.get("daily_available_minutes", 60),
        intensity=roadmap_context.get("intensity", "moderate"),
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        return result
    except (json.JSONDecodeError, Exception) as e:
        return {
            "changes": [],
            "response_message": f"변경사항을 생성하지 못했습니다: {str(e)}",
            "suggestions": ["다시 한번 구체적으로 요청해주세요."],
        }


async def process_edit_request(
    user_message: str,
    roadmap_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process a user's edit request for a roadmap.

    Args:
        user_message: User's edit request in natural language
        roadmap_context: Current roadmap data including monthly_goals, weekly_tasks, daily_tasks

    Returns:
        Dict with:
        - changes: List of proposed changes
        - response_message: Message to show to user
        - suggestions: Additional suggestions
    """
    # Step 1: Analyze intent
    analysis = await analyze_intent(user_message, roadmap_context)

    intent = analysis.get("intent", "explain")
    targets = analysis.get("targets", [])

    # Step 2: If just explanation, return understanding
    if intent == "explain":
        return {
            "changes": [],
            "response_message": analysis.get("understanding", "무엇을 도와드릴까요?"),
            "suggestions": [
                "특정 태스크를 수정하고 싶으시면 'D3 태스크 쉽게 바꿔줘'처럼 요청해주세요.",
                "태스크 추가는 '1주차에 복습 추가해줘'처럼 요청해주세요.",
            ],
        }

    # Step 3: Generate changes
    result = await generate_changes(
        user_message=user_message,
        roadmap_context=roadmap_context,
        intent=intent,
        targets=targets,
    )

    return result


# Quick action handlers
QUICK_ACTIONS = {
    "난이도 낮추기": "전체적인 학습 난이도를 낮춰주세요. 기초 개념 위주로, 실습량을 줄여주세요.",
    "세부사항 추가": "각 태스크에 더 구체적인 학습 내용과 단계를 추가해주세요.",
    "시간 줄이기": "각 태스크의 학습량을 줄여서 더 짧은 시간에 완료할 수 있게 해주세요.",
    "복습 추가": "각 주의 마지막에 복습 시간을 추가해주세요.",
}


async def process_quick_action(
    action_name: str,
    roadmap_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Process a predefined quick action."""
    if action_name not in QUICK_ACTIONS:
        return {
            "changes": [],
            "response_message": f"알 수 없는 액션입니다: {action_name}",
            "suggestions": list(QUICK_ACTIONS.keys()),
        }

    user_message = QUICK_ACTIONS[action_name]
    return await process_edit_request(user_message, roadmap_context)
