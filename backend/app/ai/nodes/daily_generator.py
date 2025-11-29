from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import DAILY_TASKS_PROMPT, DAILY_TASKS_WITH_CONTEXT_PROMPT


def daily_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate daily tasks for each weekly task."""
    llm = create_llm()

    all_daily_tasks = []

    for monthly_data in state["weekly_tasks"]:
        month_number = monthly_data["month_number"]
        monthly_daily_tasks = []

        for weekly_task in monthly_data["weekly_tasks"]:
            # Use context-aware prompt if interview context is available
            if state.get("interview_context"):
                prompt = DAILY_TASKS_WITH_CONTEXT_PROMPT.format(
                    topic=state["topic"],
                    weekly_task_title=weekly_task["title"],
                    weekly_task_description=weekly_task["description"],
                    month_number=month_number,
                    week_number=weekly_task["week_number"],
                    mode=state["mode"].value if hasattr(state["mode"], "value") else state["mode"],
                    interview_context=state["interview_context"],
                    daily_time=state.get("daily_time", "1~2시간"),
                )
            else:
                prompt = DAILY_TASKS_PROMPT.format(
                    topic=state["topic"],
                    weekly_task_title=weekly_task["title"],
                    weekly_task_description=weekly_task["description"],
                    month_number=month_number,
                    week_number=weekly_task["week_number"],
                )

            response = llm.invoke([HumanMessage(content=prompt)])

            try:
                result = parse_json_response(response.content)
                daily_tasks = result["daily_tasks"]
            except (ValueError, KeyError):
                # Generate fallback daily tasks
                daily_tasks = [
                    {
                        "day_number": i + 1,
                        "title": f"{i + 1}일차 학습" if i < 5 else f"{i + 1}일차 복습",
                        "description": f"{weekly_task['title']}의 {i + 1}일차 {'학습' if i < 5 else '복습'} 내용입니다."
                    }
                    for i in range(7)
                ]

            monthly_daily_tasks.append({
                "week_number": weekly_task["week_number"],
                "daily_tasks": daily_tasks
            })

        all_daily_tasks.append({
            "month_number": month_number,
            "weeks": monthly_daily_tasks
        })

    state["daily_tasks"] = all_daily_tasks
    return state
