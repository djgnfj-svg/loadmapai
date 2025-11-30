"""Web search node using Tavily for real-time information retrieval."""
import json
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import RoadmapGenerationState


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,
    )


def _get_tavily_search():
    """Get Tavily search tool if API key is available."""
    if not settings.tavily_api_key:
        return None

    try:
        from langchain_tavily import TavilySearchResults
        return TavilySearchResults(
            api_key=settings.tavily_api_key,
            max_results=5,
            search_depth="advanced",
            include_domains=[
                "roadmap.sh",
                "github.com",
                "coursera.org",
                "udemy.com",
                "freecodecamp.org",
                "medium.com",
                "dev.to",
                "stackoverflow.com",
            ],
        )
    except ImportError:
        return None


def _extract_level_from_context(interview_context: Optional[str]) -> str:
    """Extract user's experience level from interview context."""
    if not interview_context:
        return "beginner"

    context_lower = interview_context.lower()
    if any(word in context_lower for word in ["고급", "경험 있", "실무", "advanced", "expert"]):
        return "advanced"
    elif any(word in context_lower for word in ["중급", "intermediate", "어느 정도", "조금"]):
        return "intermediate"
    return "beginner"


def _generate_search_queries(topic: str, level: str, mode: str) -> List[str]:
    """Generate search queries based on topic and user level."""
    queries = [
        f"{topic} learning roadmap 2025",
        f"best {topic} courses for {level} 2025",
        f"{topic} tutorial step by step guide",
    ]

    if mode == "learning":
        queries.append(f"{topic} study plan curriculum")
    else:  # planning mode
        queries.append(f"{topic} project ideas portfolio")

    return queries


def synthesize_search_context(results: List[Dict[str, Any]], topic: str) -> str:
    """Synthesize search results into a context string for roadmap generation.

    Public wrapper for use by streaming endpoints.

    Args:
        results: List of search result dictionaries with title, content, url
        topic: The learning topic

    Returns:
        Synthesized context string with key learning information
    """
    return _synthesize_search_results(results, topic)


def _synthesize_search_results(results: List[Dict[str, Any]], topic: str) -> str:
    """Synthesize search results into a context string."""
    if not results:
        return ""

    llm = create_llm()

    # Format results for LLM
    results_text = ""
    for i, result in enumerate(results[:10], 1):
        title = result.get("title", "")
        content = result.get("content", "")[:500]
        url = result.get("url", "")
        results_text += f"\n{i}. {title}\n   URL: {url}\n   내용: {content}\n"

    synthesis_prompt = f"""다음은 "{topic}" 학습에 대한 웹 검색 결과입니다.

{results_text}

위 검색 결과를 바탕으로 "{topic}" 학습 로드맵 생성에 유용한 정보를 요약해주세요:
1. 추천 학습 경로나 커리큘럼
2. 필수 선행 지식
3. 추천 학습 자료 (강의, 책 등)
4. 최신 트렌드나 주의사항

간결하게 bullet point로 정리해주세요. 한국어로 작성하세요."""

    try:
        response = llm.invoke([HumanMessage(content=synthesis_prompt)])
        return response.content
    except Exception as e:
        # Fallback: just list the titles
        return "\n".join([f"- {r.get('title', '')}" for r in results[:5]])


# ============ Public Search Functions ============

def search_learning_resources(topic: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Search for learning resources related to a topic.

    Used by streaming endpoints for roadmap generation.

    Args:
        topic: The learning topic to search for
        num_results: Maximum number of results to return

    Returns:
        List of search result dictionaries with title, content, url
    """
    search_tool = _get_tavily_search()

    if not search_tool:
        return []

    try:
        query = f"{topic} learning roadmap curriculum best practices 2025"
        results = search_tool.invoke(query)

        if isinstance(results, list):
            return results[:num_results]
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []


def web_searcher(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Search the web for relevant learning resources and roadmaps.

    This node searches for:
    - Learning roadmaps and curricula
    - Recommended courses and tutorials
    - Latest trends and best practices

    Results are synthesized and added to state for use by other nodes.
    """
    search_tool = _get_tavily_search()

    # If no Tavily API key, skip web search
    if not search_tool:
        state["search_results"] = []
        state["search_context"] = ""
        return state

    topic = state["topic"]
    mode = state["mode"].value if hasattr(state["mode"], "value") else state["mode"]
    interview_context = state.get("interview_context", "")
    level = _extract_level_from_context(interview_context)

    # Generate and execute search queries
    queries = _generate_search_queries(topic, level, mode)
    all_results = []

    for query in queries:
        try:
            results = search_tool.invoke(query)
            if isinstance(results, list):
                all_results.extend(results)
        except Exception as e:
            # Log error but continue with other queries
            print(f"Search error for query '{query}': {e}")
            continue

    # Deduplicate results by URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    # Store raw results
    state["search_results"] = unique_results[:15]

    # Synthesize results into context
    if unique_results:
        state["search_context"] = _synthesize_search_results(unique_results, topic)
    else:
        state["search_context"] = ""

    return state
