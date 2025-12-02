"""Unified LLM utilities for AI nodes."""
import json
import logging
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings

logger = logging.getLogger(__name__)

# DEV_MODE에 따라 모델 선택 (비용 절약)
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
CLAUDE_MODEL = "claude-3-5-haiku-20241022" if DEV_MODE else "claude-sonnet-4-5-20250929"

logger.info(f"[AI] Claude model: {CLAUDE_MODEL} (DEV_MODE={DEV_MODE})")


def create_llm(temperature: float = 0.7) -> ChatAnthropic:
    """Create a Claude LLM instance."""
    return ChatAnthropic(
        model=CLAUDE_MODEL,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=temperature,
        max_tokens=8192,  # 더 긴 응답 허용
    )


def parse_json_response(content: str) -> dict:
    """Parse JSON from AI response, handling markdown code blocks."""
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    return json.loads(content.strip())


def invoke_llm_json(prompt: str, temperature: float = 0.7) -> dict:
    """Invoke LLM and parse JSON response."""
    llm = create_llm(temperature)
    response = llm.invoke([HumanMessage(content=prompt)])
    return parse_json_response(response.content)
