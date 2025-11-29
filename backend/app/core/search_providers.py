"""Web search provider implementations.

Concrete implementations of the WebSearchProvider interface.
"""
from typing import List

from app.config import settings
from app.core.interfaces import WebSearchProvider, SearchResult, Result


class TavilySearchProvider(WebSearchProvider):
    """Tavily API search provider implementation."""

    def __init__(self, api_key: str = None):
        self._api_key = api_key or settings.tavily_api_key

    def search(self, query: str, num_results: int = 10) -> Result[List[SearchResult]]:
        """Perform search using Tavily API."""
        if not self._api_key:
            return Result.failure("Tavily API key not configured")

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self._api_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=num_results,
            )

            results = []
            for item in response.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    score=item.get("score", 0.0),
                ))

            return Result.success(results)

        except ImportError:
            return Result.failure("Tavily package not installed")
        except Exception as e:
            return Result.failure(f"Search failed: {str(e)}")


class MockSearchProvider(WebSearchProvider):
    """Mock search provider for testing."""

    def __init__(self, default_results: List[SearchResult] = None):
        self._default_results = default_results or [
            SearchResult(
                title="Mock Result",
                url="https://example.com",
                snippet="This is a mock search result for testing.",
                score=1.0,
            )
        ]
        self._call_count = 0
        self._last_query: str = None

    def search(self, query: str, num_results: int = 10) -> Result[List[SearchResult]]:
        """Return mock search results."""
        self._call_count += 1
        self._last_query = query
        return Result.success(self._default_results[:num_results])

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def last_query(self) -> str:
        return self._last_query


# ============ Factory Function ============

def create_search_provider(
    provider_type: str = "tavily",
    **kwargs
) -> WebSearchProvider:
    """Factory function to create search providers.

    Args:
        provider_type: Type of provider ("tavily", "mock")
        **kwargs: Provider-specific arguments

    Returns:
        WebSearchProvider instance
    """
    providers = {
        "tavily": TavilySearchProvider,
        "mock": MockSearchProvider,
    }

    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")

    return providers[provider_type](**kwargs)
