from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import WEEKLY_TASKS_PROMPT, WEEKLY_TASKS_WITH_CONTEXT_PROMPT


def weekly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate weekly tasks for each monthly goal."""
    llm = create_llm()

    all_weekly_tasks = []

    for monthly_goal in state["monthly_goals"]:
        # Use context-aware prompt if interview context is available
        if state.get("interview_context"):
            prompt = WEEKLY_TASKS_WITH_CONTEXT_PROMPT.format(
                topic=state["topic"],
                monthly_goal_title=monthly_goal["title"],
                monthly_goal_description=monthly_goal["description"],
                month_number=monthly_goal["month_number"],
                mode=state["mode"].value if hasattr(state["mode"], "value") else state["mode"],
                interview_context=state["interview_context"],
            )
        else:
            prompt = WEEKLY_TASKS_PROMPT.format(
                topic=state["topic"],
                monthly_goal_title=monthly_goal["title"],
                monthly_goal_description=monthly_goal["description"],
                month_number=monthly_goal["month_number"],
            )

        response = llm.invoke([HumanMessage(content=prompt)])

        try:
            result = parse_json_response(response.content)
            weekly_tasks = result["weekly_tasks"]
        except (ValueError, KeyError):
            # Generate fallback weekly tasks
            weekly_tasks = [
                {
                    "week_number": i + 1,
                    "title": f"{i + 1}주차 학습",
                    "description": f"{monthly_goal['title']}의 {i + 1}주차 학습 과제입니다."
                }
                for i in range(4)
            ]

        all_weekly_tasks.append({
            "month_number": monthly_goal["month_number"],
            "weekly_tasks": weekly_tasks
        })

    state["weekly_tasks"] = all_weekly_tasks
    return state
