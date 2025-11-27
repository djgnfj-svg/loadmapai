import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import WEEKLY_TASKS_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


def weekly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate weekly tasks for each monthly goal."""
    llm = create_llm()

    all_weekly_tasks = []

    for monthly_goal in state["monthly_goals"]:
        prompt = WEEKLY_TASKS_PROMPT.format(
            topic=state["topic"],
            monthly_goal_title=monthly_goal["title"],
            monthly_goal_description=monthly_goal["description"],
            month_number=monthly_goal["month_number"],
        )

        response = llm.invoke([HumanMessage(content=prompt)])

        try:
            result = json.loads(response.content)
            weekly_tasks = result["weekly_tasks"]
        except (json.JSONDecodeError, KeyError):
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
