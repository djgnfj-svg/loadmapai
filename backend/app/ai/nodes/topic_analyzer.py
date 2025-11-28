import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import QuestionGenerationState
from app.ai.prompts.templates import TOPIC_ANALYSIS_PROMPT


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.5,
    )


def topic_analyzer(state: QuestionGenerationState) -> QuestionGenerationState:
    """Analyze the daily task topic to prepare for question generation."""
    llm = create_llm()

    prompt = TOPIC_ANALYSIS_PROMPT.format(
        roadmap_topic=state["roadmap_topic"],
        monthly_goal_title=state["monthly_goal_title"],
        weekly_task_title=state["weekly_task_title"],
        daily_task_title=state["daily_task_title"],
        daily_task_description=state["daily_task_description"],
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
        state["key_concepts"] = result.get("key_concepts", [])
        state["difficulty_level"] = result.get("difficulty_level", "intermediate")
        state["question_focus_areas"] = result.get("question_focus_areas", [])
    except (json.JSONDecodeError, KeyError):
        # Fallback defaults
        state["key_concepts"] = [state["daily_task_title"]]
        state["difficulty_level"] = "intermediate"
        state["question_focus_areas"] = [state["weekly_task_title"]]

    return state
