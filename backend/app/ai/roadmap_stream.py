"""Streaming roadmap generation with SSE events.

SSE 스트리밍을 통해 로드맵 생성 과정을 실시간으로 전송합니다.
기존 roadmap_graph.py와 달리 월별로 순차 생성하여 각 단계마다 이벤트를 발송합니다.

생성 순서:
1. 제목/설명 생성 → title_ready
2. 1월 목표 생성 → month_ready
3. 1월 주간 과제 생성 → weeks_ready
4. 2월 목표 생성 → month_ready
... (반복)
N. DB 저장 → complete
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator, Any
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.ai.llm import invoke_llm_json
from app.ai.prompts.templates import ROADMAP_TITLE_PROMPT, build_interview_section
from app.ai.prompts.streaming_templates import (
    SINGLE_MONTH_GOAL_PROMPT,
    SINGLE_MONTH_WEEKS_PROMPT,
)
from app.models import Roadmap, MonthlyGoal, WeeklyTask
from app.models.roadmap import RoadmapMode

# Thread pool for running sync LLM calls in async context
_executor = ThreadPoolExecutor(max_workers=4)


async def generate_roadmap_streaming(
    topic: str,
    duration_months: int,
    start_date,
    mode: RoadmapMode,
    user_id: str,
    db: Session,
    interview_context: dict = None,
) -> AsyncGenerator[dict, None]:
    """Generate roadmap with streaming events.

    Args:
        topic: 학습 주제
        duration_months: 기간 (1-6개월)
        start_date: 시작 날짜
        mode: 로드맵 모드
        user_id: 사용자 ID
        db: DB 세션
        interview_context: SMART 인터뷰 컨텍스트 (선택)

    Yields:
        dict: SSE 이벤트 {"type": "event_name", "data": {...}}
    """
    interview_section = build_interview_section(interview_context)
    loop = asyncio.get_event_loop()

    # 진행률 계산: 1(제목) + 2*개월수(월+주)
    total_steps = 1 + (2 * duration_months)
    current_step = 0

    # 축적할 데이터
    title = None
    description = None
    monthly_goals = []
    weekly_tasks = []

    try:
        # Step 1: 제목 생성
        current_step += 1
        title_result = await loop.run_in_executor(
            _executor,
            _generate_title,
            topic,
            duration_months,
            interview_section,
        )
        title = title_result["title"]
        description = title_result["description"]

        yield {
            "type": "title_ready",
            "data": {"title": title, "description": description}
        }
        yield _progress_event(current_step, total_steps, "제목 생성 완료")

        # 각 월별로 목표 → 주간 순서로 생성
        for month_num in range(1, duration_months + 1):
            # Step N: 월별 목표 생성
            current_step += 1
            month_result = await loop.run_in_executor(
                _executor,
                _generate_single_month,
                topic,
                title,
                month_num,
                duration_months,
                monthly_goals,
                interview_section,
            )
            monthly_goals.append(month_result)

            yield {
                "type": "month_ready",
                "data": month_result
            }
            yield _progress_event(current_step, total_steps, f"{month_num}월 목표 생성 완료")

            # Step N+1: 해당 월의 주간 과제 생성
            current_step += 1
            weeks_result = await loop.run_in_executor(
                _executor,
                _generate_single_month_weeks,
                topic,
                month_result,
                month_num,
                interview_section,
            )
            weekly_tasks.append({
                "month_number": month_num,
                "weeks": weeks_result
            })

            yield {
                "type": "weeks_ready",
                "data": {
                    "month_number": month_num,
                    "weeks": weeks_result
                }
            }
            yield _progress_event(current_step, total_steps, f"{month_num}월 주간 과제 생성 완료")

        # DB 저장
        roadmap_id = _save_roadmap(
            topic=topic,
            title=title,
            description=description,
            duration_months=duration_months,
            start_date=start_date,
            mode=mode,
            user_id=user_id,
            monthly_goals=monthly_goals,
            weekly_tasks=weekly_tasks,
            db=db,
        )

        # 첫 주 일일 태스크 생성
        try:
            await _generate_first_week_daily_tasks(
                roadmap_id, user_id, db, interview_context
            )
        except Exception as e:
            # 일일 태스크 생성 실패는 경고만 (전체 실패 아님)
            yield {
                "type": "warning",
                "data": {"message": f"첫 주 일일 태스크 생성 실패: {str(e)}"}
            }

        yield {
            "type": "complete",
            "data": {
                "roadmap_id": roadmap_id,
                "title": title,
                "is_finalized": False
            }
        }

    except Exception as e:
        yield {
            "type": "error",
            "data": {
                "message": str(e),
                "recoverable": False
            }
        }


def _progress_event(current: int, total: int, message: str) -> dict:
    """Create a progress event."""
    return {
        "type": "progress",
        "data": {
            "current_step": current,
            "total_steps": total,
            "percentage": round((current / total) * 100),
            "message": message
        }
    }


def _generate_title(topic: str, duration_months: int, interview_section: str) -> dict:
    """Generate title and description."""
    prompt = ROADMAP_TITLE_PROMPT.format(
        topic=topic,
        duration_months=duration_months,
        interview_section=interview_section,
    )
    try:
        return invoke_llm_json(prompt, temperature=0.7)
    except Exception:
        # Fallback
        return {
            "title": f"{topic} 학습 로드맵",
            "description": f"{duration_months}개월 동안 {topic}을(를) 체계적으로 학습합니다."
        }


def _generate_single_month(
    topic: str,
    roadmap_title: str,
    month_number: int,
    duration_months: int,
    previous_months: list,
    interview_section: str,
) -> dict:
    """Generate a single month's goal."""
    prompt = SINGLE_MONTH_GOAL_PROMPT.format(
        topic=topic,
        roadmap_title=roadmap_title,
        month_number=month_number,
        duration_months=duration_months,
        previous_months_summary=_format_previous_months(previous_months),
        interview_section=interview_section,
    )
    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        result["month_number"] = month_number
        return result
    except Exception:
        # Fallback with more specific content based on month
        if month_number == 1:
            phase = "기초 개념과 핵심 원리"
            phase_desc = "핵심 개념을 이해하고 기본기를 다지며 실습 환경을 구축합니다."
        elif month_number == duration_months:
            phase = "실전 프로젝트와 종합 활용"
            phase_desc = "학습한 내용을 종합하여 실전 프로젝트를 완성하고 포트폴리오를 구축합니다."
        else:
            phase = "심화 학습과 응용"
            phase_desc = "기초를 바탕으로 심화 내용을 학습하고 다양한 응용 사례를 실습합니다."

        return {
            "month_number": month_number,
            "title": f"{topic} {phase}",
            "description": phase_desc
        }


def _generate_single_month_weeks(
    topic: str,
    month_goal: dict,
    month_number: int,
    interview_section: str,
) -> list:
    """Generate weekly tasks for a single month."""
    prompt = SINGLE_MONTH_WEEKS_PROMPT.format(
        topic=topic,
        month_number=month_number,
        month_title=month_goal["title"],
        month_description=month_goal["description"],
        interview_section=interview_section,
    )
    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        weeks = result.get("weeks", [])
        # week_number 확인 및 보정
        for i, week in enumerate(weeks):
            if "week_number" not in week:
                week["week_number"] = i + 1
        return weeks[:4]  # 최대 4주
    except Exception:
        # Fallback with more meaningful weekly structure
        week_templates = [
            ("개념 이해와 환경 설정", "기본 개념을 학습하고 실습 환경을 구축합니다. 핵심 용어와 기초 원리를 이해합니다."),
            ("핵심 기능 학습", "주요 기능을 단계별로 학습하고 간단한 예제를 통해 실습합니다."),
            ("심화 학습과 실습", "고급 기능을 학습하고 실제 사례를 분석하며 응용 실습을 진행합니다."),
            ("종합 프로젝트와 복습", "학습한 내용을 종합하여 미니 프로젝트를 완성하고 전체 내용을 복습합니다."),
        ]
        return [
            {
                "week_number": w + 1,
                "title": f"{month_goal['title']} - {week_templates[w][0]}",
                "description": week_templates[w][1]
            }
            for w in range(4)
        ]


def _format_previous_months(months: list) -> str:
    """Format previous months for context."""
    if not months:
        return "없음 (첫 번째 월입니다)"
    return "\n".join([
        f"- {m['month_number']}월: {m['title']} - {m['description']}"
        for m in months
    ])


def _save_roadmap(
    topic: str,
    title: str,
    description: str,
    duration_months: int,
    start_date,
    mode: RoadmapMode,
    user_id: str,
    monthly_goals: list,
    weekly_tasks: list,
    db: Session,
) -> str:
    """Save the generated roadmap to the database.

    Returns:
        str: 생성된 로드맵 ID
    """
    end_date = start_date + relativedelta(months=duration_months)

    roadmap = Roadmap(
        user_id=UUID(user_id),
        title=title,
        description=description,
        topic=topic,
        duration_months=duration_months,
        start_date=start_date,
        end_date=end_date,
        mode=mode,
        is_finalized=False,  # 확정 전 상태로 저장
    )
    db.add(roadmap)
    db.flush()

    for monthly_data in monthly_goals:
        monthly_goal = MonthlyGoal(
            roadmap_id=roadmap.id,
            month_number=monthly_data["month_number"],
            title=monthly_data["title"],
            description=monthly_data["description"],
        )
        db.add(monthly_goal)
        db.flush()

        # 해당 월의 주간 과제 찾기
        weekly_month = next(
            (w for w in weekly_tasks if w["month_number"] == monthly_data["month_number"]),
            None
        )

        if weekly_month and "weeks" in weekly_month:
            for week_data in weekly_month["weeks"]:
                weekly_task = WeeklyTask(
                    monthly_goal_id=monthly_goal.id,
                    week_number=week_data["week_number"],
                    title=week_data["title"],
                    description=week_data["description"],
                )
                db.add(weekly_task)
                db.flush()

    db.commit()
    return str(roadmap.id)


async def _generate_first_week_daily_tasks(
    roadmap_id: str,
    user_id: str,
    db: Session,
    interview_context: dict = None,
):
    """Generate daily tasks for the first week of the roadmap."""
    from app.services.daily_generation_service import DailyGenerationService

    first_week = (
        db.query(WeeklyTask)
        .join(MonthlyGoal)
        .filter(
            MonthlyGoal.roadmap_id == UUID(roadmap_id),
            MonthlyGoal.month_number == 1,
            WeeklyTask.week_number == 1,
        )
        .first()
    )

    if first_week:
        service = DailyGenerationService(db)
        await service.generate_daily_tasks_for_week(
            first_week.id,
            UUID(user_id),
            force=True,
            interview_context=interview_context,
        )
