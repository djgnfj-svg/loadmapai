"""Base classes for AI nodes following SOLID principles.

This module provides:
- Abstract base class for all AI processing nodes (OCP)
- Common functionality shared across nodes
- Dependency injection for LLM providers (DIP)
- Consistent error handling patterns
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar
import logging

from app.core.interfaces import LLMProvider, Result
from app.core.llm_providers import get_default_llm_provider

# Type variable for state
StateT = TypeVar("StateT", bound=Dict[str, Any])

logger = logging.getLogger(__name__)


class BaseNode(ABC, Generic[StateT]):
    """Abstract base class for AI processing nodes.

    Provides:
    - Consistent interface for all nodes
    - Dependency injection for LLM provider
    - Common error handling
    - Logging

    Subclasses must implement:
    - name: Property returning node identifier
    - _process_impl: Core processing logic
    """

    def __init__(self, llm_provider: LLMProvider = None):
        """Initialize node with optional LLM provider.

        Args:
            llm_provider: LLM provider for AI operations.
                         Uses default provider if not specified.
        """
        self._llm = llm_provider or get_default_llm_provider()

    @property
    @abstractmethod
    def name(self) -> str:
        """Node identifier for logging and debugging."""
        pass

    @property
    def temperature(self) -> float:
        """Default LLM temperature for this node.

        Override in subclasses for different behaviors:
        - 0.3: Evaluation, grading (more deterministic)
        - 0.5: Analysis (balanced)
        - 0.7: Generation (more creative, default)
        """
        return 0.7

    @abstractmethod
    def _process_impl(self, state: StateT) -> Result[StateT]:
        """Core processing logic to be implemented by subclasses.

        Args:
            state: Current workflow state

        Returns:
            Result containing updated state or error
        """
        pass

    def process(self, state: StateT) -> Result[StateT]:
        """Process state with error handling and logging.

        Wraps _process_impl with common error handling.

        Args:
            state: Current workflow state

        Returns:
            Result containing updated state or error
        """
        logger.debug(f"[{self.name}] Starting processing")

        try:
            result = self._process_impl(state)

            if result.is_success:
                logger.debug(f"[{self.name}] Processing completed successfully")
            else:
                logger.warning(f"[{self.name}] Processing failed: {result.error}")

            return result

        except Exception as e:
            logger.exception(f"[{self.name}] Unexpected error: {str(e)}")
            return Result.failure(f"노드 처리 중 오류: {str(e)}")

    def __call__(self, state: StateT) -> StateT:
        """Allow node to be called directly for LangGraph compatibility.

        LangGraph expects nodes to raise exceptions or return updated state.
        This converts our Result pattern to that interface.
        """
        result = self.process(state)

        if result.is_error:
            # Store error in state instead of raising
            state["error_message"] = result.error
            state["retry_count"] = state.get("retry_count", 0) + 1
            return state

        return result.value if result.value else state

    def invoke_llm(self, prompt: str, temperature: float = None) -> Result[str]:
        """Invoke LLM with prompt.

        Args:
            prompt: The prompt to send
            temperature: Override default temperature

        Returns:
            Result containing raw response or error
        """
        temp = temperature if temperature is not None else self.temperature
        return self._llm.invoke(prompt, temp)

    def invoke_llm_json(self, prompt: str, temperature: float = None) -> Result[Dict[str, Any]]:
        """Invoke LLM and parse JSON response.

        Args:
            prompt: The prompt to send
            temperature: Override default temperature

        Returns:
            Result containing parsed JSON or error
        """
        temp = temperature if temperature is not None else self.temperature
        return self._llm.invoke_json(prompt, temp)


class GeneratorNode(BaseNode[StateT]):
    """Base class for content generation nodes.

    Used for nodes that generate content:
    - Monthly goals
    - Weekly tasks
    - Daily tasks
    - Questions
    """

    @property
    def temperature(self) -> float:
        """Higher temperature for creative generation."""
        return 0.7

    def _get_fallback(self, state: StateT) -> Any:
        """Get fallback content when generation fails.

        Override in subclasses to provide specific fallbacks.
        """
        return None


class AnalyzerNode(BaseNode[StateT]):
    """Base class for analysis nodes.

    Used for nodes that analyze content:
    - Topic analysis
    - Goal analysis
    - Answer evaluation
    """

    @property
    def temperature(self) -> float:
        """Balanced temperature for analysis."""
        return 0.5


class EvaluatorNode(BaseNode[StateT]):
    """Base class for evaluation/grading nodes.

    Used for nodes that evaluate or grade:
    - Answer grading
    - Quality validation
    """

    @property
    def temperature(self) -> float:
        """Lower temperature for consistent evaluation."""
        return 0.3


class ValidatorNode(BaseNode[StateT]):
    """Base class for validation nodes.

    Used for nodes that validate generated content.
    Typically doesn't need LLM (validation is logic-based).
    """

    @property
    def temperature(self) -> float:
        """Not typically used, but low for consistency."""
        return 0.2

    def _process_impl(self, state: StateT) -> Result[StateT]:
        """Validate state and return result.

        Override in subclasses for specific validation logic.
        """
        issues = self._validate(state)

        if issues:
            state["validation_passed"] = False
            state["error_message"] = "; ".join(issues)
            state["retry_count"] = state.get("retry_count", 0) + 1
            return Result.success(state)

        state["validation_passed"] = True
        state["error_message"] = None
        return Result.success(state)

    @abstractmethod
    def _validate(self, state: StateT) -> list[str]:
        """Perform validation and return list of issues.

        Returns:
            Empty list if valid, list of issue descriptions otherwise.
        """
        pass


class CompositeNode(BaseNode[StateT]):
    """Node that composes multiple sub-nodes.

    Useful for creating complex processing pipelines
    that can be reused as a single unit.
    """

    def __init__(
        self,
        nodes: list[BaseNode],
        llm_provider: LLMProvider = None,
    ):
        super().__init__(llm_provider)
        self._nodes = nodes

    @property
    def name(self) -> str:
        return f"Composite({', '.join(n.name for n in self._nodes)})"

    def _process_impl(self, state: StateT) -> Result[StateT]:
        """Process state through all sub-nodes in sequence."""
        current_state = state

        for node in self._nodes:
            result = node.process(current_state)
            if result.is_error:
                return result
            current_state = result.value

        return Result.success(current_state)
