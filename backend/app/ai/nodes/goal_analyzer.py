import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import (
    ROADMAP_TITLE_PROMPT,
    ROADMAP_TITLE_WITH_CONTEXT_PROMPT,
    ROADMAP_TITLE_WITH_SEARCH_PROMPT,
)


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7,
    )


def goal_analyzer(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Analyze the topic and generate roadmap title and description."""
    llm = create_llm()

    # Choose prompt based on available context
    interview_context = state.get("interview_context")
    search_context = state.get("search_context")
    mode = state["mode"].value if hasattr(state["mode"], "value") else state["mode"]

    if interview_context and search_context:
        # Full context with interview and web search
        prompt = ROADMAP_TITLE_WITH_SEARCH_PROMPT.format(
            topic=state["topic"],
            duration_months=state["duration_months"],
            mode=mode,
            interview_context=interview_context,
            search_context=search_context,
        )
    elif interview_context:
        # Interview context only
        prompt = ROADMAP_TITLE_WITH_CONTEXT_PROMPT.format(
            topic=state["topic"],
            duration_months=state["duration_months"],
            mode=mode,
            interview_context=interview_context,
        )
    else:
        # Basic prompt
        prompt = ROADMAP_TITLE_PROMPT.format(
            topic=state["topic"],
            duration_months=state["duration_months"],
        )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
        state["title"] = result["title"]
        state["description"] = result["description"]
    except (json.JSONDecodeError, KeyError) as e:
        state["error_message"] = f"Failed to parse goal analysis: {str(e)}"
        state["title"] = f"{state['topic']} 학습 로드맵"
        state["description"] = f"{state['duration_months']}개월 동안 {state['topic']}을(를) 체계적으로 학습하는 로드맵입니다."

    return state
