from langchain_core.messages import HumanMessage

from app.ai.llm import create_llm, parse_json_response
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import MONTHLY_GOALS_PROMPT


def monthly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate monthly goals for the roadmap."""
    llm = create_llm()

    prompt = MONTHLY_GOALS_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
        title=state["title"],
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = parse_json_response(response.content)
        state["monthly_goals"] = result["monthly_goals"]
    except (ValueError, KeyError) as e:
        state["error_message"] = f"Failed to parse monthly goals: {str(e)}"
        # Generate fallback monthly goals
        state["monthly_goals"] = [
            {
                "month_number": i + 1,
                "title": f"{i + 1}개월차: {state['topic']} 기초" if i == 0 else f"{i + 1}개월차: {state['topic']} 심화",
                "description": f"{state['topic']}의 {'기초' if i == 0 else '심화'} 내용을 학습합니다."
            }
            for i in range(state["duration_months"])
        ]

    return state
