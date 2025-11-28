"""Server-Sent Events (SSE) streaming utilities."""
import json
import asyncio
from typing import AsyncGenerator, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class StreamEventType(str, Enum):
    """Types of streaming events."""
    # General
    START = "start"
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"

    # Interview specific
    GENERATING_QUESTIONS = "generating_questions"
    EVALUATING_ANSWERS = "evaluating_answers"
    GENERATING_FOLLOWUP = "generating_followup"
    ADVANCING_STAGE = "advancing_stage"
    COMPILING_CONTEXT = "compiling_context"

    # Roadmap specific
    WEB_SEARCHING = "web_searching"
    WEB_SEARCH_RESULT = "web_search_result"
    ANALYZING_GOALS = "analyzing_goals"
    GOALS_ANALYZED = "goals_analyzed"  # With title/description
    GENERATING_MONTHLY = "generating_monthly"
    MONTHLY_GENERATED = "monthly_generated"  # With month data
    GENERATING_WEEKLY = "generating_weekly"
    WEEKLY_GENERATED = "weekly_generated"  # With week data
    GENERATING_DAILY = "generating_daily"
    DAILY_GENERATED = "daily_generated"  # With daily data
    VALIDATING = "validating"
    SAVING = "saving"


@dataclass
class StreamEvent:
    """A streaming event to send to the client."""
    event_type: StreamEventType
    message: str
    data: Optional[dict] = None
    progress: Optional[int] = None  # 0-100

    def to_sse(self) -> str:
        """Convert to SSE format."""
        event_data = {
            "type": self.event_type.value,
            "message": self.message,
        }
        if self.data:
            event_data["data"] = self.data
        if self.progress is not None:
            event_data["progress"] = self.progress

        return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"


class StreamingManager:
    """Manages streaming events for a single request."""

    def __init__(self):
        self._queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self._is_complete = False

    async def emit(
        self,
        event_type: StreamEventType,
        message: str,
        data: Optional[dict] = None,
        progress: Optional[int] = None,
    ):
        """Emit a streaming event."""
        event = StreamEvent(
            event_type=event_type,
            message=message,
            data=data,
            progress=progress,
        )
        await self._queue.put(event)

    async def complete(self, data: Optional[dict] = None):
        """Mark the stream as complete."""
        await self.emit(StreamEventType.COMPLETE, "완료", data=data, progress=100)
        self._is_complete = True

    async def error(self, message: str):
        """Emit an error event."""
        await self.emit(StreamEventType.ERROR, message)
        self._is_complete = True

    async def stream(self) -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        while not self._is_complete:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield event.to_sse()

                if event.event_type in (StreamEventType.COMPLETE, StreamEventType.ERROR):
                    break
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"


# Global registry for active streams (for thread-safe callback access)
_active_streams: dict[str, StreamingManager] = {}


def get_stream(stream_id: str) -> Optional[StreamingManager]:
    """Get an active stream by ID."""
    return _active_streams.get(stream_id)


def register_stream(stream_id: str, manager: StreamingManager):
    """Register a stream manager."""
    _active_streams[stream_id] = manager


def unregister_stream(stream_id: str):
    """Unregister a stream manager."""
    _active_streams.pop(stream_id, None)
