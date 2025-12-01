"""Core interfaces and protocols for dependency inversion.

This module defines abstract interfaces that allow for:
- Loose coupling between components
- Easy testing with mock implementations
- Swappable implementations (e.g., different LLM providers)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum


# ============ Result Pattern for Error Handling ============

class ResultStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"


T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """Result pattern for explicit error handling without exceptions.

    Usage:
        result = service.do_something()
        if result.is_success:
            data = result.value
        else:
            handle_error(result.error)
    """
    status: ResultStatus
    value: Optional[T] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        return self.status != ResultStatus.SUCCESS

    @classmethod
    def success(cls, value: T, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.SUCCESS, value=value, details=details)

    @classmethod
    def failure(cls, error: str, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.ERROR, error=error, details=details)

    @classmethod
    def validation_error(cls, error: str, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.VALIDATION_ERROR, error=error, details=details)

    @classmethod
    def not_found(cls, error: str = "Resource not found") -> "Result[T]":
        return cls(status=ResultStatus.NOT_FOUND, error=error)


# ============ LLM Provider Interface ============

class LLMProvider(ABC):
    """Abstract interface for LLM providers.

    Allows swapping between different LLM backends:
    - Anthropic Claude
    - OpenAI GPT
    - Local models
    - Mock for testing
    """

    @abstractmethod
    def invoke(self, prompt: str, temperature: float = 0.7) -> Result[str]:
        """Invoke the LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Controls randomness (0.0-1.0)

        Returns:
            Result containing raw response string or error
        """
        pass

    @abstractmethod
    def invoke_json(self, prompt: str, temperature: float = 0.7) -> Result[Dict[str, Any]]:
        """Invoke the LLM and parse JSON response.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Controls randomness (0.0-1.0)

        Returns:
            Result containing parsed JSON dict or error
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the current model."""
        pass


# ============ Web Search Interface ============

@dataclass
class SearchResult:
    """Represents a single search result."""
    title: str
    url: str
    snippet: str
    score: float = 0.0


class WebSearchProvider(ABC):
    """Abstract interface for web search providers.

    Allows swapping between:
    - Tavily API
    - Google Search API
    - Bing Search API
    - Mock for testing
    """

    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> Result[List[SearchResult]]:
        """Perform a web search.

        Args:
            query: Search query string
            num_results: Maximum number of results

        Returns:
            Result containing list of SearchResult or error
        """
        pass


# ============ Repository Interface ============

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


class Repository(ABC, Generic[EntityT, IdT]):
    """Abstract repository pattern for data access.

    Provides a consistent interface for CRUD operations
    across different entity types.
    """

    @abstractmethod
    def get_by_id(self, entity_id: IdT) -> Optional[EntityT]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[EntityT]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    def create(self, entity: EntityT) -> EntityT:
        """Create a new entity."""
        pass

    @abstractmethod
    def update(self, entity: EntityT) -> EntityT:
        """Update an existing entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: IdT) -> bool:
        """Delete an entity by ID."""
        pass


# ============ AI Node Interface ============

StateT = TypeVar("StateT", bound=Dict[str, Any])


class AINode(ABC, Generic[StateT]):
    """Abstract base class for AI processing nodes.

    Provides consistent interface for all AI nodes in the pipeline.
    Enables:
    - Uniform error handling
    - Consistent logging
    - Easy testing
    - Dependency injection of LLM provider
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    @property
    @abstractmethod
    def name(self) -> str:
        """Node name for logging and identification."""
        pass

    @property
    def temperature(self) -> float:
        """Default temperature for this node. Override in subclasses."""
        return 0.7

    @abstractmethod
    def process(self, state: StateT) -> Result[StateT]:
        """Process the state and return updated state.

        Args:
            state: Current workflow state

        Returns:
            Result containing updated state or error
        """
        pass

    def __call__(self, state: StateT) -> StateT:
        """Allow node to be called directly for LangGraph compatibility.

        Converts Result pattern to exception-based flow for LangGraph.
        """
        result = self.process(state)
        if result.is_error:
            state["error_message"] = result.error
        elif result.value:
            return result.value
        return state
