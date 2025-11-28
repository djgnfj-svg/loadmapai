"""Streaming API endpoints for real-time AI progress updates."""
import asyncio
import uuid
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.interview_session import InterviewStatus
from app.api.deps import get_current_user
from app.core.streaming import (
    StreamingManager,
    StreamEventType,
    register_stream,
    unregister_stream,
)
from app.ai.callbacks import InterviewStreamingHandler, RoadmapStreamingHandler
from app.services.interview_service import InterviewService
from app.schemas.interview import InterviewStartRequest, InterviewSubmitAnswersRequest

router = APIRouter()


@router.post("/interviews/start")
async def start_interview_streaming(
    request: InterviewStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start interview with real-time streaming progress."""
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    async def generate():
        try:
            loop = asyncio.get_event_loop()
            handler = InterviewStreamingHandler(stream_id, loop)

            # Emit start
            await manager.emit(
                StreamEventType.START,
                "인터뷰를 시작합니다...",
                progress=0
            )

            service = InterviewService(db)

            # Create session
            await manager.emit(
                StreamEventType.PROGRESS,
                "세션 생성 중...",
                progress=10
            )

            session = service.create_session(
                user_id=current_user.id,
                topic=request.topic,
                mode=request.mode,
                duration_months=request.duration_months,
            )

            # Generate questions with streaming
            handler.emit_generating_questions()

            from app.ai.interview_graph import start_interview as start_interview_graph

            result = start_interview_graph(
                topic=request.topic,
                mode=request.mode,
                duration_months=request.duration_months,
                user_id=str(current_user.id),
                session_id=str(session.id),
                callbacks=[handler],
            )

            # Update DB
            await manager.emit(
                StreamEventType.PROGRESS,
                "저장 중...",
                progress=90
            )
            service.update_session_state(session, result["state"])

            # Complete
            await manager.complete(data={
                "session_id": str(session.id),
                "current_stage": result["current_stage"],
                "questions": result["questions"],
            })

        except Exception as e:
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    background_tasks.add_task(generate)

    return StreamingResponse(
        manager.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/interviews/{session_id}/submit")
async def submit_answers_streaming(
    session_id: str,
    request: InterviewSubmitAnswersRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit interview answers with real-time streaming progress."""
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    async def generate():
        try:
            loop = asyncio.get_event_loop()
            handler = InterviewStreamingHandler(stream_id, loop)

            service = InterviewService(db)

            # Get session
            session = service.get_session(session_id, current_user.id)
            if not session:
                await manager.error("인터뷰 세션을 찾을 수 없습니다.")
                return

            if session.status != InterviewStatus.IN_PROGRESS:
                await manager.error("이미 완료되거나 취소된 인터뷰입니다.")
                return

            await manager.emit(
                StreamEventType.START,
                "답변을 분석합니다...",
                progress=0
            )

            # Evaluate answers
            handler.emit_evaluating()

            state = service.session_to_state(session)
            answers = [
                {"question_id": a.question_id, "answer": a.answer}
                for a in request.answers
            ]

            from app.ai.interview_graph import submit_answers as submit_answers_graph

            result = submit_answers_graph(state, answers, callbacks=[handler])

            # Update stage progress
            if result["is_complete"]:
                handler.emit_compiling()
            else:
                handler.emit_stage_progress(
                    result["current_stage"],
                    result.get("stage_name", ""),
                    70
                )

            # Save
            await manager.emit(
                StreamEventType.PROGRESS,
                "저장 중...",
                progress=90
            )
            service.update_session_state(session, result["state"])

            # Complete
            if result["is_complete"]:
                await manager.complete(data={
                    "session_id": str(session.id),
                    "is_complete": True,
                    "compiled_context": result.get("compiled_context", ""),
                    "key_insights": result.get("key_insights", []),
                    "schedule": result.get("schedule", {}),
                })
            else:
                await manager.complete(data={
                    "session_id": str(session.id),
                    "is_complete": False,
                    "current_stage": result["current_stage"],
                    "questions": result["questions"],
                    "is_followup": session.followup_count > 0,
                })

        except Exception as e:
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    background_tasks.add_task(generate)

    return StreamingResponse(
        manager.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/roadmaps/generate")
async def generate_roadmap_streaming(
    interview_session_id: str,
    start_date: str,
    use_web_search: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate roadmap from interview with real-time streaming progress."""
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    async def generate():
        try:
            loop = asyncio.get_event_loop()
            handler = RoadmapStreamingHandler(stream_id, loop)

            service = InterviewService(db)

            # Get interview session
            session = service.get_session(interview_session_id, current_user.id)
            if not session:
                await manager.error("인터뷰 세션을 찾을 수 없습니다.")
                return

            if not session.is_complete:
                await manager.error("완료된 인터뷰만 로드맵을 생성할 수 있습니다.")
                return

            await manager.emit(
                StreamEventType.START,
                "맞춤형 로드맵 생성을 시작합니다...",
                progress=0
            )

            # Web search if enabled
            if use_web_search:
                handler.emit_web_search_start(session.topic)

                from app.ai.nodes.web_searcher import search_learning_resources
                search_results = search_learning_resources(session.topic, num_results=10)

                if search_results:
                    handler.emit_web_search_result(search_results)

            # Analyze goals
            handler.emit_analyzing_goals()

            # Generate roadmap
            from app.ai.roadmap_graph import generate_roadmap_from_interview

            roadmap_data = await generate_roadmap_from_interview(
                session=session,
                start_date=date.fromisoformat(start_date),
                use_web_search=use_web_search,
                callbacks=[handler],
                progress_callback=lambda msg, pct: asyncio.run_coroutine_threadsafe(
                    manager.emit(StreamEventType.PROGRESS, msg, progress=pct),
                    loop
                )
            )

            # Save to DB
            handler.emit_saving()

            from app.services.roadmap_service import RoadmapService
            roadmap_service = RoadmapService(db)

            roadmap = roadmap_service.create_roadmap_from_data(
                user_id=current_user.id,
                roadmap_data=roadmap_data,
                interview_session_id=session.id,
            )

            # Update interview session with roadmap ID
            session.roadmap_id = roadmap.id
            db.commit()

            await manager.complete(data={
                "roadmap_id": str(roadmap.id),
                "title": roadmap.title,
            })

        except Exception as e:
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    background_tasks.add_task(generate)

    return StreamingResponse(
        manager.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
