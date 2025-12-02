"""Goal analyzer node - generates title and description."""
from app.ai.llm import invoke_llm_json
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import ROADMAP_TITLE_PROMPT


def goal_analyzer(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Generate roadmap title and description."""
    prompt = ROADMAP_TITLE_PROMPT.format(
        topic=state["topic"],
        duration_months=state["duration_months"],
    )

    try:
        result = invoke_llm_json(prompt, temperature=0.7)
        state["title"] = result["title"]
        state["description"] = result["description"]
    except Exception as e:
        # Fallback
        state["title"] = f"{state['topic']} 학습 로드맵"
        state["description"] = f"{state['duration_months']}개월 동안 {state['topic']}을(를) 체계적으로 학습합니다."
        state["error_message"] = str(e)

    return state
