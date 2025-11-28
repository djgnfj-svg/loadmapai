"""Tests for web searcher node."""

import pytest
from unittest.mock import patch, MagicMock

from app.ai.nodes.web_searcher import search_learning_resources


class TestWebSearcher:
    """Test web search functionality."""

    @patch("app.ai.nodes.web_searcher.TavilySearchResults")
    def test_search_learning_resources(self, mock_tavily):
        """Test searching for learning resources."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = [
            {
                "title": "Learn Python",
                "url": "https://example.com/python",
                "content": "Python tutorial for beginners...",
            },
            {
                "title": "Python Course",
                "url": "https://example.com/course",
                "content": "Advanced Python course...",
            },
        ]
        mock_tavily.return_value = mock_instance

        result = search_learning_resources("Python 학습", num_results=5)

        assert result is not None
        assert len(result) > 0
        mock_instance.invoke.assert_called_once()

    @patch("app.ai.nodes.web_searcher.TavilySearchResults")
    def test_search_learning_resources_empty(self, mock_tavily):
        """Test searching with no results."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = []
        mock_tavily.return_value = mock_instance

        result = search_learning_resources("very obscure topic")

        assert result is not None
        assert len(result) == 0

    @patch("app.ai.nodes.web_searcher.TavilySearchResults")
    def test_search_handles_exception(self, mock_tavily):
        """Test that search handles exceptions gracefully."""
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = Exception("API Error")
        mock_tavily.return_value = mock_instance

        # Should not raise, returns empty list
        result = search_learning_resources("Python")
        assert result == []

    @patch("app.ai.nodes.web_searcher.TavilySearchResults")
    @patch("app.ai.nodes.web_searcher.ChatAnthropic")
    def test_synthesize_with_web_search(self, mock_anthropic, mock_tavily):
        """Test synthesizing web search results."""
        from app.ai.nodes.web_searcher import synthesize_with_web_search

        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = [
            {"title": "Resource 1", "url": "https://example.com", "content": "Content 1"}
        ]
        mock_tavily.return_value = mock_tavily_instance

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Synthesized context")
        mock_anthropic.return_value = mock_llm

        result = synthesize_with_web_search("Python 학습", 3)

        assert result is not None
        assert "Synthesized context" in result or len(result) > 0
