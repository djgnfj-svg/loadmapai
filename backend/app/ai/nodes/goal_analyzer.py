"""Goal analyzer node for roadmap generation.

Analyzes the topic and generates roadmap title and description.
"""
from app.ai.base import AnalyzerNode
from app.ai.state import RoadmapGenerationState
from app.ai.prompts.templates import ROADMAP_TITLE_PROMPT
from app.core.interfaces import LLMProvider, Result


class GoalAnalyzerNode(AnalyzerNode[RoadmapGenerationState]):
    """Analyzes topic and generates roadmap title/description."""

    @property
    def name(self) -> str:
        return "GoalAnalyzer"

    def _build_prompt(self, state: RoadmapGenerationState) -> str:
        """Build prompt for roadmap title generation."""
        return ROADMAP_TITLE_PROMPT.format(
            topic=state["topic"],
            duration_months=state["duration_months"],
        )

    def _get_fallback(self, state: RoadmapGenerationState) -> dict:
        """Generate fallback title/description on failure."""
        return {
            "title": f"{state['topic']} 학습 로드맵",
            "description": f"{state['duration_months']}개월 동안 {state['topic']}을(를) 체계적으로 학습하는 로드맵입니다.",
        }

    def _process_impl(self, state: RoadmapGenerationState) -> Result[RoadmapGenerationState]:
        """Analyze topic and generate title/description."""
        prompt = self._build_prompt(state)
        result = self.invoke_llm_json(prompt)

        if result.is_error:
            fallback = self._get_fallback(state)
            state["title"] = fallback["title"]
            state["description"] = fallback["description"]
            state["error_message"] = result.error
            return Result.success(state)

        try:
            data = result.value
            state["title"] = data["title"]
            state["description"] = data["description"]
            return Result.success(state)
        except KeyError as e:
            fallback = self._get_fallback(state)
            state["title"] = fallback["title"]
            state["description"] = fallback["description"]
            state["error_message"] = f"Missing key in response: {e}"
            return Result.success(state)


# ============ Factory Function for LangGraph ============

_node_instance: GoalAnalyzerNode = None


def get_goal_analyzer_node(llm_provider: LLMProvider = None) -> GoalAnalyzerNode:
    """Get or create goal analyzer node instance."""
    global _node_instance
    if _node_instance is None or llm_provider is not None:
        _node_instance = GoalAnalyzerNode(llm_provider)
    return _node_instance


def goal_analyzer(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """LangGraph-compatible function wrapper.

    Maintains backward compatibility with existing graph definitions.
    """
    node = get_goal_analyzer_node()
    return node(state)
