"""LangChain callbacks for streaming progress updates."""
import asyncio
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage

from app.core.streaming import StreamingManager, StreamEventType, get_stream


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler that emits streaming events."""

    def __init__(self, stream_id: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.stream_id = stream_id
        self.loop = loop or asyncio.get_event_loop()
        self._current_step = ""
        self._token_buffer = ""

    def _emit_sync(
        self,
        event_type: StreamEventType,
        message: str,
        data: Optional[dict] = None,
        progress: Optional[int] = None,
    ):
        """Emit event synchronously (for use in sync callbacks)."""
        manager = get_stream(self.stream_id)
        if manager:
            asyncio.run_coroutine_threadsafe(
                manager.emit(event_type, message, data, progress),
                self.loop
            )

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when LLM starts."""
        # Determine what we're doing based on tags or metadata
        step = "AI 응답 생성 중"
        if tags:
            if "questions" in tags:
                step = "질문 생성 중"
            elif "evaluation" in tags:
                step = "답변 분석 중"
            elif "followup" in tags:
                step = "추가 질문 생성 중"
            elif "context" in tags:
                step = "컨텍스트 정리 중"
            elif "goals" in tags:
                step = "학습 목표 분석 중"
            elif "monthly" in tags:
                step = "월간 계획 생성 중"
            elif "weekly" in tags:
                step = "주간 계획 생성 중"
            elif "daily" in tags:
                step = "일일 계획 생성 중"

        self._current_step = step
        self._emit_sync(StreamEventType.PROGRESS, step)

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Any] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when LLM generates a new token (streaming)."""
        self._token_buffer += token
        # Emit partial content every few tokens for smoother UX
        if len(self._token_buffer) > 50:
            self._emit_sync(
                StreamEventType.PROGRESS,
                self._current_step,
                data={"partial": self._token_buffer[-100:]}  # Last 100 chars
            )
            self._token_buffer = ""

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when LLM finishes."""
        self._token_buffer = ""

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when LLM errors."""
        self._emit_sync(StreamEventType.ERROR, f"AI 오류: {str(error)}")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool starts."""
        tool_name = serialized.get("name", "도구")
        if "search" in tool_name.lower() or "tavily" in tool_name.lower():
            self._emit_sync(
                StreamEventType.WEB_SEARCHING,
                "웹에서 최신 학습 자료 검색 중...",
            )

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool finishes."""
        # If it was a search, emit results
        if isinstance(output, list) and len(output) > 0:
            self._emit_sync(
                StreamEventType.WEB_SEARCH_RESULT,
                f"검색 결과 {len(output)}개 발견",
                data={"count": len(output)}
            )


class InterviewStreamingHandler(StreamingCallbackHandler):
    """Specialized handler for interview streaming."""

    def emit_stage_progress(self, stage: int, stage_name: str, progress: int):
        """Emit interview stage progress."""
        self._emit_sync(
            StreamEventType.ADVANCING_STAGE,
            f"Stage {stage}: {stage_name}",
            data={"stage": stage, "stage_name": stage_name},
            progress=progress
        )

    def emit_generating_questions(self, count: int = 0):
        """Emit that questions are being generated."""
        self._emit_sync(
            StreamEventType.GENERATING_QUESTIONS,
            "맞춤형 질문 생성 중...",
            data={"count": count}
        )

    def emit_evaluating(self):
        """Emit that answers are being evaluated."""
        self._emit_sync(
            StreamEventType.EVALUATING_ANSWERS,
            "답변 분석 중...",
        )

    def emit_compiling(self):
        """Emit that context is being compiled."""
        self._emit_sync(
            StreamEventType.COMPILING_CONTEXT,
            "인터뷰 결과 정리 중...",
            progress=90
        )


class RoadmapStreamingHandler(StreamingCallbackHandler):
    """Specialized handler for roadmap generation streaming."""

    def emit_web_search_start(self, query: str):
        """Emit web search start."""
        self._emit_sync(
            StreamEventType.WEB_SEARCHING,
            f"'{query}' 관련 최신 자료 검색 중...",
        )

    def emit_web_search_result(self, results: List[dict]):
        """Emit web search results."""
        titles = [r.get("title", "")[:30] for r in results[:3]]
        self._emit_sync(
            StreamEventType.WEB_SEARCH_RESULT,
            f"검색 완료: {len(results)}개 자료 발견",
            data={"count": len(results), "titles": titles}
        )

    def emit_analyzing_goals(self):
        """Emit goal analysis start."""
        self._emit_sync(
            StreamEventType.ANALYZING_GOALS,
            "학습 목표 분석 중...",
            progress=20
        )

    def emit_goals_analyzed(self, title: str, description: str):
        """Emit goals analyzed with roadmap title/description."""
        self._emit_sync(
            StreamEventType.GOALS_ANALYZED,
            "목표 분석 완료",
            data={"title": title, "description": description},
            progress=25
        )

    def emit_generating_monthly(self, month: int, total: int):
        """Emit monthly goal generation."""
        self._emit_sync(
            StreamEventType.GENERATING_MONTHLY,
            f"월간 계획 생성 중... ({month}/{total})",
            data={"month": month, "total": total},
            progress=25 + int((month / total) * 25)  # 25-50%
        )

    def emit_monthly_generated(self, month_data: dict):
        """Emit generated monthly goal data."""
        self._emit_sync(
            StreamEventType.MONTHLY_GENERATED,
            f"{month_data.get('month_number', '?')}월 계획 완료",
            data={"monthly": month_data},
            progress=25 + int((month_data.get('month_number', 1) / month_data.get('total', 1)) * 25)
        )

    def emit_generating_weekly(self, week: int, total: int, month: int):
        """Emit weekly task generation."""
        self._emit_sync(
            StreamEventType.GENERATING_WEEKLY,
            f"주간 계획 생성 중... ({month}월 {week}주차)",
            data={"week": week, "total": total, "month": month},
            progress=50 + int((week / max(total, 1)) * 25)  # 50-75%
        )

    def emit_weekly_generated(self, week_data: dict, month_number: int):
        """Emit generated weekly task data."""
        self._emit_sync(
            StreamEventType.WEEKLY_GENERATED,
            f"{month_number}월 {week_data.get('week_number', '?')}주차 완료",
            data={"weekly": week_data, "month_number": month_number},
        )

    def emit_generating_daily(self, progress_pct: int, month: int = 0, week: int = 0):
        """Emit daily task generation."""
        self._emit_sync(
            StreamEventType.GENERATING_DAILY,
            f"일일 학습 계획 생성 중... ({month}월 {week}주차)",
            data={"month": month, "week": week},
            progress=75 + int(progress_pct * 0.15)  # 75-90%
        )

    def emit_daily_generated(self, daily_tasks: List[dict], month_number: int, week_number: int):
        """Emit generated daily tasks data."""
        self._emit_sync(
            StreamEventType.DAILY_GENERATED,
            f"{month_number}월 {week_number}주차 일일 계획 완료",
            data={
                "daily_tasks": daily_tasks,
                "month_number": month_number,
                "week_number": week_number
            },
        )

    def emit_validating(self):
        """Emit validation start."""
        self._emit_sync(
            StreamEventType.VALIDATING,
            "로드맵 검증 중...",
            progress=90
        )

    def emit_saving(self):
        """Emit saving start."""
        self._emit_sync(
            StreamEventType.SAVING,
            "저장 중...",
            progress=95
        )
