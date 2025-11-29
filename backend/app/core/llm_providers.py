"""LLM provider implementations.

Concrete implementations of the LLMProvider interface.
"""
import json
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.core.interfaces import LLMProvider, Result


class ClaudeLLMProvider(LLMProvider):
    """Anthropic Claude LLM provider implementation.

    Uses Claude Sonnet 4.5 by default.
    """

    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

    def __init__(self, model: str = None, api_key: str = None):
        self._model = model or self.DEFAULT_MODEL
        self._api_key = api_key or settings.anthropic_api_key
        self._llm_cache: Dict[float, ChatAnthropic] = {}

    def _get_llm(self, temperature: float) -> ChatAnthropic:
        """Get or create LLM instance for given temperature."""
        if temperature not in self._llm_cache:
            self._llm_cache[temperature] = ChatAnthropic(
                model=self._model,
                anthropic_api_key=self._api_key,
                temperature=temperature,
            )
        return self._llm_cache[temperature]

    def invoke(self, prompt: str, temperature: float = 0.7) -> Result[str]:
        """Invoke Claude and return raw response."""
        try:
            llm = self._get_llm(temperature)
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content if hasattr(response, 'content') else str(response)
            return Result.success(content)
        except Exception as e:
            return Result.failure(f"LLM invocation failed: {str(e)}")

    def invoke_json(self, prompt: str, temperature: float = 0.7) -> Result[Dict[str, Any]]:
        """Invoke Claude and parse JSON response."""
        result = self.invoke(prompt, temperature)
        if result.is_error:
            return Result.failure(result.error)

        try:
            parsed = self._parse_json_response(result.value)
            return Result.success(parsed)
        except json.JSONDecodeError as e:
            return Result.failure(f"JSON parsing failed: {str(e)}")

    def get_model_name(self) -> str:
        return self._model

    @staticmethod
    def _parse_json_response(content: str) -> Dict[str, Any]:
        """Parse JSON from response, handling markdown code blocks."""
        # Strip markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing.

    Returns predefined responses based on prompt patterns.
    """

    def __init__(self, default_response: Dict[str, Any] = None):
        self._default_response = default_response or {"status": "mock"}
        self._responses: Dict[str, Dict[str, Any]] = {}
        self._call_count = 0
        self._last_prompt: str = None

    def set_response(self, pattern: str, response: Dict[str, Any]) -> None:
        """Set a response for prompts containing the pattern."""
        self._responses[pattern] = response

    def invoke(self, prompt: str, temperature: float = 0.7) -> Result[str]:
        """Return mock response as JSON string."""
        self._call_count += 1
        self._last_prompt = prompt
        response = self._get_response_for_prompt(prompt)
        return Result.success(json.dumps(response, ensure_ascii=False))

    def invoke_json(self, prompt: str, temperature: float = 0.7) -> Result[Dict[str, Any]]:
        """Return mock response as dict."""
        self._call_count += 1
        self._last_prompt = prompt
        response = self._get_response_for_prompt(prompt)
        return Result.success(response)

    def get_model_name(self) -> str:
        return "mock-llm"

    def _get_response_for_prompt(self, prompt: str) -> Dict[str, Any]:
        """Find matching response or return default."""
        for pattern, response in self._responses.items():
            if pattern in prompt:
                return response
        return self._default_response

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def last_prompt(self) -> str:
        return self._last_prompt


# ============ Factory Function ============

def create_llm_provider(
    provider_type: str = "claude",
    **kwargs
) -> LLMProvider:
    """Factory function to create LLM providers.

    Args:
        provider_type: Type of provider ("claude", "mock")
        **kwargs: Provider-specific arguments

    Returns:
        LLMProvider instance
    """
    providers = {
        "claude": ClaudeLLMProvider,
        "mock": MockLLMProvider,
    }

    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")

    return providers[provider_type](**kwargs)


# ============ Default Provider Instance ============

# Singleton-like default provider for backward compatibility
_default_provider: LLMProvider = None


def get_default_llm_provider() -> LLMProvider:
    """Get or create the default LLM provider."""
    global _default_provider
    if _default_provider is None:
        _default_provider = ClaudeLLMProvider()
    return _default_provider


def set_default_llm_provider(provider: LLMProvider) -> None:
    """Set the default LLM provider (useful for testing)."""
    global _default_provider
    _default_provider = provider
