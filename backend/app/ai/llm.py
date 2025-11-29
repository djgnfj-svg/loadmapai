"""Centralized LLM utilities for AI nodes.

This module provides:
- Unified LLM instance creation with configurable temperature
- JSON response parsing with markdown code block handling
- Consistent error handling patterns
"""
import json
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings


# Default model for all AI operations
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def create_llm(temperature: float = 0.7) -> ChatAnthropic:
    """Create a Claude LLM instance.

    Args:
        temperature: Controls randomness. Lower = more focused, higher = more creative.
            - 0.3: Evaluation, grading, validation
            - 0.5: Analysis, topic understanding
            - 0.7: Generation, creative content (default)
    """
    return ChatAnthropic(
        model=DEFAULT_MODEL,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=temperature,
    )


def parse_json_response(content: str) -> dict:
    """Parse JSON from AI response, handling markdown code blocks.

    Claude often wraps JSON in ```json ... ``` blocks. This function
    strips those blocks before parsing.

    Args:
        content: Raw response content from LLM

    Returns:
        Parsed JSON as dictionary

    Raises:
        json.JSONDecodeError: If content is not valid JSON
    """
    # Strip markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    return json.loads(content.strip())


def invoke_llm(prompt: str, temperature: float = 0.7) -> dict:
    """Invoke LLM and parse JSON response.

    Convenience function that combines LLM creation, invocation,
    and JSON parsing.

    Args:
        prompt: The prompt to send to the LLM
        temperature: LLM temperature setting

    Returns:
        Parsed JSON response as dictionary

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    llm = create_llm(temperature)
    response = llm.invoke([HumanMessage(content=prompt)])
    return parse_json_response(response.content)
