"""Feedback analysis and roadmap modification logic."""
import logging
from typing import List, Optional

from app.ai.llm import invoke_llm_json, DEFAULT_ANALYTICAL_TEMP
from app.ai.prompts.feedback_prompts import (
    FEEDBACK_ANALYSIS_PROMPT,
    format_roadmap_compact,
    format_recent_messages,
    build_interview_section,
)

logger = logging.getLogger(__name__)


def analyze_and_modify_roadmap(
    user_message: str,
    roadmap_data: dict,
    messages: List[dict],
    interview_context: Optional[dict] = None,
) -> dict:
    """사용자 피드백을 분석하고 로드맵을 수정합니다.

    Args:
        user_message: 사용자 메시지
        roadmap_data: 현재 로드맵 데이터
        messages: 이전 대화 히스토리
        interview_context: SMART 인터뷰 컨텍스트 (선택)

    Returns:
        dict: {
            "response": str,  # AI 응답 메시지
            "modification_type": str,  # none/weekly/monthly/both
            "modifications": {
                "monthly_goals": [...],
                "weekly_tasks": [...]
            }
        }
    """
    # 프롬프트 구성
    roadmap_json = format_roadmap_compact(roadmap_data)
    recent_messages = format_recent_messages(messages, limit=5)
    interview_section = build_interview_section(interview_context)

    prompt = FEEDBACK_ANALYSIS_PROMPT.format(
        roadmap_json=roadmap_json,
        interview_section=interview_section,
        recent_messages=recent_messages,
        user_message=user_message,
    )

    try:
        # LLM 호출 (분석적 온도 사용)
        result = invoke_llm_json(prompt, temperature=DEFAULT_ANALYTICAL_TEMP)

        # 결과 검증 및 기본값 설정
        return {
            "response": result.get("response", "피드백을 반영했습니다."),
            "modification_type": result.get("modification_type", "none"),
            "modifications": {
                "monthly_goals": result.get("modifications", {}).get("monthly_goals", []),
                "weekly_tasks": result.get("modifications", {}).get("weekly_tasks", []),
            }
        }

    except Exception as e:
        logger.error(f"Failed to analyze feedback: {e}")
        # 폴백 응답
        return {
            "response": "죄송합니다. 피드백 처리 중 문제가 발생했어요. 다시 한번 말씀해주시겠어요?",
            "modification_type": "none",
            "modifications": {
                "monthly_goals": [],
                "weekly_tasks": [],
            }
        }


def apply_modifications(roadmap_data: dict, modifications: dict) -> dict:
    """수정 사항을 로드맵에 적용합니다.

    Args:
        roadmap_data: 현재 로드맵 데이터
        modifications: AI가 생성한 수정 사항

    Returns:
        dict: 수정된 로드맵 데이터
    """
    updated = roadmap_data.copy()

    # Monthly goals 수정
    modified_months = modifications.get("monthly_goals", [])
    if modified_months:
        updated_goals = []
        for goal in updated.get("monthly_goals", []):
            # 수정된 버전이 있는지 확인
            modified = next(
                (m for m in modified_months if m.get("month_number") == goal.get("month_number")),
                None
            )
            if modified:
                updated_goals.append({
                    "month_number": goal.get("month_number"),
                    "title": modified.get("title", goal.get("title")),
                    "description": modified.get("description", goal.get("description")),
                })
            else:
                updated_goals.append(goal)
        updated["monthly_goals"] = updated_goals

    # Weekly tasks 수정
    modified_weeks = modifications.get("weekly_tasks", [])
    if modified_weeks:
        updated_weekly_tasks = []
        for month_tasks in updated.get("weekly_tasks", []):
            month_num = month_tasks.get("month_number")
            updated_weeks = []

            for week in month_tasks.get("weeks", []):
                week_num = week.get("week_number")
                # 수정된 버전이 있는지 확인
                modified = next(
                    (w for w in modified_weeks
                     if w.get("month_number") == month_num and w.get("week_number") == week_num),
                    None
                )
                if modified:
                    updated_weeks.append({
                        "week_number": week_num,
                        "title": modified.get("title", week.get("title")),
                        "description": modified.get("description", week.get("description")),
                    })
                else:
                    updated_weeks.append(week)

            updated_weekly_tasks.append({
                "month_number": month_num,
                "weeks": updated_weeks
            })
        updated["weekly_tasks"] = updated_weekly_tasks

    return updated
