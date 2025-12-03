"""Weekly generator node - generates ALL weekly tasks in 1 LLM call."""
from app.ai.llm import invoke_llm_json
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import WEEKLY_TASKS_PROMPT, build_interview_section


def weekly_generator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate all weekly tasks for all months in a single LLM call."""
    interview_section = build_interview_section(state.get("interview_context"))
    duration_months = state["duration_months"]

    # Build monthly goals summary
    monthly_summary = "\n".join([
        f"- {g['month_number']}개월차: {g['title']} - {g['description']}"
        for g in state["monthly_goals"]
    ])

    prompt = WEEKLY_TASKS_PROMPT.format(
        topic=state["topic"],
        duration_months=duration_months,
        monthly_goals_summary=monthly_summary,
        interview_section=interview_section,
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        weekly_tasks = result["weekly_tasks"]

        # Validate: filter to only include requested months
        weekly_tasks = [
            w for w in weekly_tasks
            if w.get("month_number", 0) <= duration_months
        ]

        # Ensure we have exactly the requested number of months
        if len(weekly_tasks) > duration_months:
            weekly_tasks = weekly_tasks[:duration_months]

        state["weekly_tasks"] = weekly_tasks
    except Exception as e:
        # Fallback: generate basic weekly tasks
        state["weekly_tasks"] = [
            {
                "month_number": month["month_number"],
                "weeks": [
                    {
                        "week_number": w + 1,
                        "title": f"{w + 1}주차 학습",
                        "description": f"{month['title']}의 {w + 1}주차 과제"
                    }
                    for w in range(4)
                ]
            }
            for month in state["monthly_goals"]
        ]
        state["error_message"] = str(e)

    return state
