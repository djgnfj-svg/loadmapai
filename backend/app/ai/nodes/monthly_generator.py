"""Monthly generator node - generates all monthly goals in 1 LLM call."""
from app.ai.llm import invoke_llm_json
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import MONTHLY_GOALS_PROMPT


def monthly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate all monthly goals in a single LLM call."""
    prompt = MONTHLY_GOALS_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
        title=state["title"],
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        state["monthly_goals"] = result["monthly_goals"]
    except Exception as e:
        # Fallback: generate basic monthly goals
        state["monthly_goals"] = [
            {
                "month_number": i + 1,
                "title": f"{i + 1}개월차: {state['topic']} {'기초' if i == 0 else '심화'}",
                "description": f"{state['topic']}의 {'기초' if i == 0 else '심화'} 내용을 학습합니다."
            }
            for i in range(state["duration_months"])
        ]
        state["error_message"] = str(e)

    return state
