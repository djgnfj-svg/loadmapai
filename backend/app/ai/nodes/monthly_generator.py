"""Monthly generator node - generates all monthly goals in 1 LLM call."""
from app.ai.llm import invoke_llm_json
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import MONTHLY_GOALS_PROMPT, build_interview_section


def monthly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate all monthly goals in a single LLM call."""
    interview_section = build_interview_section(state.get("interview_context"))
    duration_months = state["duration_months"]

    prompt = MONTHLY_GOALS_PROMPT.format(
        topic=state["topic"],
        duration_months=duration_months,
        title=state["title"],
        interview_section=interview_section,
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        monthly_goals = result["monthly_goals"]

        # Validate: filter to only include requested months
        monthly_goals = [
            g for g in monthly_goals
            if g.get("month_number", 0) <= duration_months
        ]

        # Ensure we have exactly the requested number of months
        if len(monthly_goals) > duration_months:
            monthly_goals = monthly_goals[:duration_months]

        state["monthly_goals"] = monthly_goals
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
