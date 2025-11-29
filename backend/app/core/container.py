"""Dependency Injection Container for service management.

Provides centralized dependency management following DIP:
- Singleton management for shared services
- Factory methods for transient services
- Easy testing with mock injection
- Configuration-driven provider selection
"""
from typing import Optional
import logging

from app.config import settings
from app.core.interfaces import LLMProvider, WebSearchProvider
from app.core.llm_providers import ClaudeLLMProvider, MockLLMProvider
from app.core.search_providers import TavilySearchProvider, MockSearchProvider

logger = logging.getLogger(__name__)


class Container:
    """Dependency Injection Container.

    Manages service lifecycles and provides dependency resolution.
    Supports both singleton and factory patterns.

    Usage:
        # Get default container
        container = get_container()

        # Get services
        llm = container.llm_provider
        search = container.search_provider

        # For testing
        container.set_llm_provider(MockLLMProvider())
    """

    _instance: Optional["Container"] = None

    def __init__(self):
        self._llm_provider: Optional[LLMProvider] = None
        self._search_provider: Optional[WebSearchProvider] = None
        self._test_mode = False

    @classmethod
    def get_instance(cls) -> "Container":
        """Get singleton container instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset container (useful for testing)."""
        cls._instance = None

    # ============ LLM Provider ============

    @property
    def llm_provider(self) -> LLMProvider:
        """Get LLM provider (lazy initialization)."""
        if self._llm_provider is None:
            self._llm_provider = self._create_llm_provider()
        return self._llm_provider

    def set_llm_provider(self, provider: LLMProvider) -> None:
        """Set custom LLM provider (for testing or custom config)."""
        self._llm_provider = provider
        logger.debug(f"LLM provider set to: {provider.get_model_name()}")

    def _create_llm_provider(self) -> LLMProvider:
        """Create default LLM provider based on configuration."""
        if self._test_mode:
            logger.debug("Creating MockLLMProvider for test mode")
            return MockLLMProvider()

        logger.debug(f"Creating ClaudeLLMProvider with model: {ClaudeLLMProvider.DEFAULT_MODEL}")
        return ClaudeLLMProvider()

    # ============ Search Provider ============

    @property
    def search_provider(self) -> WebSearchProvider:
        """Get web search provider (lazy initialization)."""
        if self._search_provider is None:
            self._search_provider = self._create_search_provider()
        return self._search_provider

    def set_search_provider(self, provider: WebSearchProvider) -> None:
        """Set custom search provider."""
        self._search_provider = provider
        logger.debug("Search provider updated")

    def _create_search_provider(self) -> WebSearchProvider:
        """Create default search provider based on configuration."""
        if self._test_mode:
            logger.debug("Creating MockSearchProvider for test mode")
            return MockSearchProvider()

        if not settings.tavily_api_key:
            logger.warning("Tavily API key not configured, using mock provider")
            return MockSearchProvider()

        logger.debug("Creating TavilySearchProvider")
        return TavilySearchProvider()

    # ============ Test Mode ============

    def enable_test_mode(self) -> None:
        """Enable test mode with mock providers."""
        self._test_mode = True
        self._llm_provider = None
        self._search_provider = None
        logger.info("Container test mode enabled")

    def disable_test_mode(self) -> None:
        """Disable test mode and reset to real providers."""
        self._test_mode = False
        self._llm_provider = None
        self._search_provider = None
        logger.info("Container test mode disabled")


# ============ Module-level Convenience Functions ============

def get_container() -> Container:
    """Get the singleton container instance."""
    return Container.get_instance()


def get_llm_provider() -> LLMProvider:
    """Get LLM provider from container."""
    return get_container().llm_provider


def get_search_provider() -> WebSearchProvider:
    """Get search provider from container."""
    return get_container().search_provider
