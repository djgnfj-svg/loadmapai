"""Daily generator node - generates ALL daily tasks in 1 LLM call."""
from app.ai.llm import invoke_llm_json
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import DAILY_TASKS_PROMPT


def daily_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate all daily tasks for all weeks in a single LLM call."""
    # Build weekly tasks summary
    weekly_summary_parts = []
    for monthly in state["weekly_tasks"]:
        month_num = monthly["month_number"]
        for week in monthly["weeks"]:
            weekly_summary_parts.append(
                f"- {month_num}개월차 {week['week_number']}주차: {week['title']} - {week['description']}"
            )
    weekly_summary = "\n".join(weekly_summary_parts)

    prompt = DAILY_TASKS_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
        weekly_tasks_summary=weekly_summary,
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        state["daily_tasks"] = result["daily_tasks"]
    except Exception as e:
        # Fallback: generate basic daily tasks
        state["daily_tasks"] = []
        for monthly in state["weekly_tasks"]:
            for week in monthly["weeks"]:
                state["daily_tasks"].append({
                    "month_number": monthly["month_number"],
                    "week_number": week["week_number"],
                    "days": [
                        {
                            "day_number": d + 1,
                            "tasks": [
                                {"title": f"이론 학습", "description": f"{week['title']} 관련 개념 학습"},
                                {"title": f"실습", "description": f"{week['title']} 실습 과제"},
                            ] if d < 5 else [
                                {"title": f"복습", "description": f"이번 주 학습 내용 복습"},
                            ]
                        }
                        for d in range(7)
                    ]
                })
        state["error_message"] = str(e)

    return state
