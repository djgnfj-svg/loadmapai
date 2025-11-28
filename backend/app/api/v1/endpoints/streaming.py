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
    """Generate roadmap from interview with real-time streaming progress.

    This endpoint streams partial roadmap data as it's generated,
    allowing the frontend to progressively render the roadmap.
    """
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

            # Import node functions
            from app.ai.nodes.web_searcher import web_searcher, synthesize_search_context
            from app.ai.nodes.goal_analyzer import goal_analyzer
            from app.ai.nodes.monthly_generator import monthly_generator
            from app.ai.nodes.weekly_generator import weekly_generator as weekly_gen_node
            from app.ai.nodes.daily_generator import daily_generator as daily_gen_node
            from app.ai.nodes.validator import validator
            from app.ai.state import RoadmapGenerationState
            from app.models.roadmap import RoadmapMode

            # Initialize state
            state: RoadmapGenerationState = {
                "topic": session.topic,
                "duration_months": session.duration_months,
                "start_date": date.fromisoformat(start_date),
                "mode": RoadmapMode(session.mode) if isinstance(session.mode, str) else session.mode,
                "user_id": str(current_user.id),
                "interview_context": session.compiled_context,
                "daily_time": f"{session.extracted_daily_minutes}분" if session.extracted_daily_minutes else None,
                "daily_available_minutes": session.extracted_daily_minutes,
                "rest_days": session.extracted_rest_days or [],
                "intensity": session.extracted_intensity or "moderate",
                "search_results": None,
                "search_context": None,
                "title": None,
                "description": None,
                "monthly_goals": [],
                "weekly_tasks": [],
                "daily_tasks": [],
                "current_month": 1,
                "current_week": 1,
                "validation_passed": False,
                "error_message": None,
                "retry_count": 0,
                "roadmap_id": None,
            }

            # Step 1: Web search (if enabled)
            if use_web_search:
                handler.emit_web_search_start(session.topic)

                from app.ai.nodes.web_searcher import search_learning_resources
                search_results = search_learning_resources(session.topic, num_results=10)

                if search_results:
                    state["search_results"] = search_results
                    state["search_context"] = synthesize_search_context(search_results, session.topic)
                    handler.emit_web_search_result(search_results)

            # Step 2: Goal analysis
            handler.emit_analyzing_goals()
            state = goal_analyzer(state)

            # Emit goals analyzed with title/description
            handler.emit_goals_analyzed(
                state.get("title", ""),
                state.get("description", "")
            )

            # Step 3: Monthly generation (with per-month streaming)
            total_months = state["duration_months"]
            handler.emit_generating_monthly(1, total_months)
            state = monthly_generator(state)

            # Emit each monthly goal
            for monthly in state.get("monthly_goals", []):
                monthly["total"] = total_months
                handler.emit_monthly_generated(monthly)

            # Step 4: Weekly generation (with per-week streaming)
            total_weeks = total_months * 4
            week_count = 0

            # We need to call weekly_generator which processes all months
            # But we can emit events after getting the result
            for month_idx, monthly in enumerate(state.get("monthly_goals", [])):
                month_num = monthly.get("month_number", month_idx + 1)
                handler.emit_generating_weekly(1, 4, month_num)

            state = weekly_gen_node(state)

            # Emit each weekly task
            for monthly_data in state.get("weekly_tasks", []):
                month_num = monthly_data.get("month_number", 1)
                for weekly in monthly_data.get("weekly_tasks", []):
                    week_count += 1
                    handler.emit_weekly_generated(weekly, month_num)

            # Step 5: Daily generation (with progress streaming)
            total_items = sum(
                len(m.get("weekly_tasks", []))
                for m in state.get("weekly_tasks", [])
            )
            current_item = 0

            for monthly_data in state.get("weekly_tasks", []):
                month_num = monthly_data.get("month_number", 1)
                for weekly in monthly_data.get("weekly_tasks", []):
                    current_item += 1
                    progress_pct = int((current_item / max(total_items, 1)) * 100)
                    handler.emit_generating_daily(progress_pct, month_num, weekly.get("week_number", 1))

            state = daily_gen_node(state)

            # Emit each daily task set
            for monthly_daily in state.get("daily_tasks", []):
                month_num = monthly_daily.get("month_number", 1)
                for week_data in monthly_daily.get("weeks", []):
                    week_num = week_data.get("week_number", 1)
                    daily_tasks = week_data.get("daily_tasks", [])
                    handler.emit_daily_generated(daily_tasks, month_num, week_num)

            # Step 6: Validation
            handler.emit_validating()
            state = validator(state)

            # Step 7: Save to DB
            handler.emit_saving()

            from app.services.roadmap_service import RoadmapService
            roadmap_service = RoadmapService(db)

            # Prepare roadmap data
            roadmap_data = {
                "topic": state["topic"],
                "title": state["title"],
                "description": state["description"],
                "duration_months": state["duration_months"],
                "start_date": state["start_date"],
                "mode": state["mode"],
                "daily_available_minutes": state.get("daily_available_minutes"),
                "rest_days": state.get("rest_days"),
                "intensity": state.get("intensity"),
                "monthly_goals": state["monthly_goals"],
                "weekly_tasks": state["weekly_tasks"],
                "daily_tasks": state["daily_tasks"],
            }

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
            import traceback
            traceback.print_exc()
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
