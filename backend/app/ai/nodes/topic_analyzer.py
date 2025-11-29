from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.state import QuestionGenerationState
from app.ai.prompts.templates import TOPIC_ANALYSIS_PROMPT


def topic_analyzer(state: QuestionGenerationState) -> QuestionGenerationState:
    """Analyze the daily task topic to prepare for question generation."""
    llm = create_llm(temperature=0.5)

    prompt = TOPIC_ANALYSIS_PROMPT.format(
        roadmap_topic=state["roadmap_topic"],
        monthly_goal_title=state["monthly_goal_title"],
        weekly_task_title=state["weekly_task_title"],
        daily_task_title=state["daily_task_title"],
        daily_task_description=state["daily_task_description"],
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = parse_json_response(response.content)
        state["key_concepts"] = result.get("key_concepts", [])
        state["difficulty_level"] = result.get("difficulty_level", "intermediate")
        state["question_focus_areas"] = result.get("question_focus_areas", [])
    except (ValueError, KeyError):
        # Fallback defaults
        state["key_concepts"] = [state["daily_task_title"]]
        state["difficulty_level"] = "intermediate"
        state["question_focus_areas"] = [state["weekly_task_title"]]

    return state
