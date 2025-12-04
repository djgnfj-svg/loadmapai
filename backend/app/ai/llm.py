"""Unified LLM utilities for AI nodes.

Temperature Settings:
- 0.7 (DEFAULT_CREATIVE_TEMP): 창의적 콘텐츠 생성 (로드맵, 질문 생성)
- 0.5 (DEFAULT_ANALYTICAL_TEMP): 분석적 작업 (답변 분석, 분류)

사용 지침:
- 콘텐츠 생성: 0.7 사용 (다양성 필요)
- 분석/분류: 0.5 사용 (일관성 필요)
"""
import json
import logging
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings

logger = logging.getLogger(__name__)

# Temperature constants
DEFAULT_CREATIVE_TEMP = 0.7   # 로드맵 생성, 질문 생성 등
DEFAULT_ANALYTICAL_TEMP = 0.5  # 답변 분석, 분류 작업 등

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
CLAUDE_MODEL = "claude-3-5-haiku-20241022" if DEV_MODE else "claude-sonnet-4-5-20250929"

logger.info(f"[AI] Claude model: {CLAUDE_MODEL} (DEV_MODE={DEV_MODE})")


def create_llm(temperature: float = 0.7) -> ChatAnthropic:
    """Create a Claude LLM instance."""
    return ChatAnthropic(
        model=CLAUDE_MODEL,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=temperature,
        max_tokens=8192,
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
