"""Streaming API endpoints for real-time AI progress updates."""
import asyncio
import json
import uuid
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
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
from app.ai.llm import invoke_llm
from app.ai.prompts.templates import ROADMAP_REFINEMENT_PROMPT


class SkeletonGenerateRequest(BaseModel):
    """Request model for skeleton generation."""
    topic: str
    mode: str
    duration_months: int


class RefineOnAnswerRequest(BaseModel):
    """Request model for progressive roadmap refinement (single answer - deprecated)."""
    session_id: str
    question_id: str
    answer: str


class BatchAnswersRequest(BaseModel):
    """Request model for batch answer submission with roadmap refinement."""
    session_id: str
    answers: dict[str, str]  # question_id -> answer


class RoadmapGenerateRequest(BaseModel):
    """Request model for roadmap generation from interview."""
    interview_session_id: str
    start_date: str
    use_web_search: bool = True


router = APIRouter()


@router.post("/interviews/start")
async def start_interview_streaming(
    request: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start interview with real-time streaming progress.

    Enhanced with:
    - Web search at interview start for better question context
    - SMART status tracking
    - Progressive draft roadmap
    """
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    # Capture user info before async task (to avoid session issues)
    user_id = current_user.id

    # Create session in request context and commit immediately
    service = InterviewService(db)
    session = service.create_session(
        user_id=user_id,
        topic=request.topic,
        mode=request.mode,
        duration_months=request.duration_months,
    )
    session_id = str(session.id)
    db.commit()  # Commit to persist the session

    async def generate():
        try:
            print(f"[DEBUG] generate() started for session {session_id}")
            loop = asyncio.get_event_loop()
            handler = InterviewStreamingHandler(stream_id, loop)

            # Emit start
            print("[DEBUG] Emitting START event")
            await manager.emit(
                StreamEventType.START,
                "인터뷰를 시작합니다...",
                progress=0
            )
            print("[DEBUG] START event emitted")

            # Web search at interview start (for better question context)
            search_context = ""
            await manager.emit(
                StreamEventType.WEB_SEARCH_STARTED,
                "학습 자료를 검색하고 있습니다...",
                progress=5
            )

            try:
                from app.ai.nodes.web_searcher import search_for_interview
                search_context = await loop.run_in_executor(
                    None,
                    lambda: search_for_interview(
                        topic=request.topic,
                        mode=request.mode,
                        duration_months=request.duration_months,
                    )
                )
                await manager.emit(
                    StreamEventType.WEB_SEARCH_COMPLETED,
                    "검색 완료",
                    progress=15,
                    data={"has_context": bool(search_context)}
                )
            except Exception as search_error:
                print(f"[DEBUG] Web search error (continuing): {search_error}")
                search_context = ""

            await manager.emit(
                StreamEventType.GENERATING_QUESTIONS,
                "SMART 기반 질문 생성 중...",
                progress=20
            )

            # Generate questions with streaming
            handler.emit_generating_questions()

            from app.ai.interview_graph import start_interview as start_interview_graph

            # Run LLM call in thread pool to avoid blocking
            print("[DEBUG] Starting LLM call...")
            result = await loop.run_in_executor(
                None,
                lambda: start_interview_graph(
                    topic=request.topic,
                    mode=request.mode,
                    duration_months=request.duration_months,
                    user_id=str(user_id),
                    session_id=session_id,
                    callbacks=[handler],
                    search_context=search_context,  # Pass web search context
                )
            )
            print(f"[DEBUG] LLM call completed, result keys: {result.keys() if result else 'None'}")

            # Emit SMART status
            smart_status = result.get("smart_status", {})
            await manager.emit(
                StreamEventType.SMART_STATUS_UPDATED,
                "SMART 상태 초기화",
                progress=80,
                data={"smart_status": smart_status}
            )

            # Update DB with fresh session
            await manager.emit(
                StreamEventType.PROGRESS,
                "저장 중...",
                progress=90
            )

            # Use fresh DB session for update
            from app.db.session import SessionLocal
            fresh_db = SessionLocal()
            try:
                fresh_service = InterviewService(fresh_db)
                fresh_session = fresh_service.get_session(session_id, user_id)
                if fresh_session:
                    fresh_service.update_session_state(fresh_session, result["state"])
                    fresh_db.commit()
            finally:
                fresh_db.close()

            # Complete
            print("[DEBUG] Emitting complete event")
            await manager.complete(data={
                "session_id": session_id,
                "current_round": result.get("current_round", 1),
                "questions": result["questions"],
                # SMART tracking fields
                "smart_status": smart_status,
                "smart_coverage": result.get("smart_coverage", {}),
                "key_results": result.get("key_results", []),
            })
            print("[DEBUG] Complete event emitted")

        except Exception as e:
            import traceback
            print(f"[DEBUG] Exception in generate(): {type(e).__name__}: {e}")
            traceback.print_exc()
            await manager.error(f"오류 발생: {str(e)}")
            print("[DEBUG] Error event emitted")
        finally:
            print("[DEBUG] generate() finished, unregistering stream")
            unregister_stream(stream_id)

    # Start generator task immediately (not as background task)
    asyncio.create_task(generate())

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit interview answers with real-time streaming progress."""
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    # Capture values before async task
    user_id = current_user.id
    answers_data = [
        {"question_id": a.question_id, "answer": a.answer}
        for a in request.answers
    ]
    user_wants_complete = request.user_wants_complete  # NEW: 사용자 완료 요청

    # Get session and state in request context
    service = InterviewService(db)
    session = service.get_session(session_id, user_id)
    session_state = service.session_to_state(session) if session else None
    session_status = session.status if session else None
    session_followup_count = session.followup_count if session else 0

    async def generate():
        try:
            if not session:
                await manager.error("인터뷰 세션을 찾을 수 없습니다.")
                return

            if session_status != InterviewStatus.IN_PROGRESS:
                await manager.error("이미 완료되거나 취소된 인터뷰입니다.")
                return

            loop = asyncio.get_event_loop()
            handler = InterviewStreamingHandler(stream_id, loop)

            await manager.emit(
                StreamEventType.START,
                "답변을 분석합니다...",
                progress=0
            )

            # Evaluate answers
            handler.emit_evaluating()

            from app.ai.interview_graph import submit_answers as submit_answers_graph

            result = await loop.run_in_executor(
                None,
                lambda: submit_answers_graph(
                    session_state,
                    answers_data,
                    callbacks=[handler],
                    user_wants_complete=user_wants_complete,  # NEW
                )
            )

            # Emit SMART tracking events
            smart_status = result.get("smart_status", {})
            key_results = result.get("key_results", [])
            draft_roadmap = result.get("draft_roadmap", {})

            # Emit SMART status update
            await manager.emit(
                StreamEventType.SMART_STATUS_UPDATED,
                "SMART 상태 업데이트",
                progress=50,
                data={"smart_status": smart_status}
            )

            # Emit Key Results if generated
            if key_results:
                await manager.emit(
                    StreamEventType.KEY_RESULTS_GENERATED,
                    "핵심 목표 생성 완료",
                    progress=55,
                    data={"key_results": key_results}
                )

            # Emit draft roadmap update
            if draft_roadmap:
                await manager.emit(
                    StreamEventType.DRAFT_ROADMAP_UPDATED,
                    "로드맵 초안 업데이트",
                    progress=60,
                    data={"draft_roadmap": draft_roadmap}
                )

            # Update stage progress
            if result["is_complete"]:
                handler.emit_compiling()
            else:
                # 다음 라운드 질문 준비 완료
                current_round = result.get("current_round", 1)
                await manager.emit(
                    StreamEventType.ROUND_ANALYSIS_COMPLETE,
                    f"라운드 {current_round} 분석 완료",
                    progress=70,
                    data={
                        "feedback": result.get("feedback"),
                        "information_level": result.get("information_level"),
                    }
                )

            # Save with fresh DB session
            await manager.emit(
                StreamEventType.PROGRESS,
                "저장 중...",
                progress=90
            )

            from app.db.session import SessionLocal
            fresh_db = SessionLocal()
            try:
                fresh_service = InterviewService(fresh_db)
                fresh_session = fresh_service.get_session(session_id, user_id)
                if fresh_session:
                    fresh_service.update_session_state(fresh_session, result["state"])
                    fresh_db.commit()
            finally:
                fresh_db.close()

            # Complete
            if result["is_complete"]:
                await manager.complete(data={
                    "session_id": session_id,
                    "is_complete": True,
                    "compiled_context": result.get("compiled_context", ""),
                    "key_insights": result.get("key_insights", []),
                    "schedule": result.get("schedule", {}),
                    # SMART tracking
                    "smart_status": smart_status,
                    "key_results": key_results,
                    # Feedback and draft
                    "feedback": result.get("feedback"),
                    "draft_roadmap": draft_roadmap,
                })
            else:
                await manager.complete(data={
                    "session_id": session_id,
                    "is_complete": False,
                    "current_round": result.get("current_round", 1),
                    "max_rounds": result.get("max_rounds", 10),
                    "questions": result.get("questions", []),
                    "is_followup": result.get("is_followup", False),
                    # 종료 관련
                    "is_terminated": result.get("is_terminated", False),
                    "termination_reason": result.get("termination_reason"),
                    "error_message": result.get("error_message"),
                    # SMART tracking
                    "smart_status": smart_status,
                    "key_results": key_results,
                    # 라운드 분석 결과
                    "feedback": result.get("feedback"),
                    "draft_roadmap": draft_roadmap,
                    "information_level": result.get("information_level"),
                    "ai_recommends_complete": result.get("ai_recommends_complete", False),
                    "can_complete": result.get("can_complete", False),
                    "continue_reason": result.get("continue_reason", ""),
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    # Start generator task immediately (not as background task)
    asyncio.create_task(generate())

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
    request: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate roadmap from interview with real-time streaming progress.

    This endpoint streams partial roadmap data as it's generated,
    allowing the frontend to progressively render the roadmap.
    """
    interview_session_id = request.interview_session_id
    start_date_str = request.start_date
    use_web_search = request.use_web_search
    user_id = current_user.id

    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    # Get interview session data in request context
    service = InterviewService(db)
    session = service.get_session(interview_session_id, user_id)

    # Capture session data before async task
    session_data = None
    if session and session.is_complete:
        from app.models.roadmap import RoadmapMode
        session_data = {
            "id": session.id,
            "topic": session.topic,
            "duration_months": session.duration_months,
            "mode": RoadmapMode(session.mode) if isinstance(session.mode, str) else session.mode,
            "compiled_context": session.compiled_context,
            "extracted_daily_minutes": session.extracted_daily_minutes,
            "extracted_rest_days": session.extracted_rest_days or [],
            "extracted_intensity": session.extracted_intensity or "moderate",
        }
    session_exists = session is not None
    session_is_complete = session.is_complete if session else False

    async def generate():
        try:
            if not session_exists:
                await manager.error("인터뷰 세션을 찾을 수 없습니다.")
                return

            if not session_is_complete:
                await manager.error("완료된 인터뷰만 로드맵을 생성할 수 있습니다.")
                return

            loop = asyncio.get_event_loop()
            handler = RoadmapStreamingHandler(stream_id, loop)

            await manager.emit(
                StreamEventType.START,
                "맞춤형 로드맵 생성을 시작합니다...",
                progress=0
            )

            # Import node functions
            from app.ai.nodes.web_searcher import synthesize_search_context
            from app.ai.nodes.goal_analyzer import goal_analyzer
            from app.ai.nodes.monthly_generator import monthly_generator
            from app.ai.nodes.weekly_generator import weekly_generator as weekly_gen_node
            from app.ai.nodes.daily_generator import daily_generator as daily_gen_node
            from app.ai.nodes.validator import validator
            from app.ai.state import RoadmapGenerationState

            # Initialize state from captured session data
            state: RoadmapGenerationState = {
                "topic": session_data["topic"],
                "duration_months": session_data["duration_months"],
                "start_date": date.fromisoformat(start_date_str),
                "mode": session_data["mode"],
                "user_id": str(user_id),
                "interview_context": session_data["compiled_context"],
                "daily_time": f"{session_data['extracted_daily_minutes']}분" if session_data["extracted_daily_minutes"] else None,
                "daily_available_minutes": session_data["extracted_daily_minutes"],
                "rest_days": session_data["extracted_rest_days"],
                "intensity": session_data["extracted_intensity"],
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
                handler.emit_web_search_start(session_data["topic"])

                from app.ai.nodes.web_searcher import search_learning_resources
                search_results = await loop.run_in_executor(
                    None,
                    lambda: search_learning_resources(session_data["topic"], num_results=10)
                )

                if search_results:
                    state["search_results"] = search_results
                    state["search_context"] = synthesize_search_context(search_results, session_data["topic"])
                    handler.emit_web_search_result(search_results)

            # Step 2: Goal analysis
            handler.emit_analyzing_goals()
            state = await loop.run_in_executor(None, lambda: goal_analyzer(state))

            # Emit goals analyzed with title/description
            handler.emit_goals_analyzed(
                state.get("title", ""),
                state.get("description", "")
            )

            # Step 3: Monthly generation (with per-month streaming)
            total_months = state["duration_months"]
            handler.emit_generating_monthly(1, total_months)
            state = await loop.run_in_executor(None, lambda: monthly_generator(state))

            # Emit each monthly goal
            for monthly in state.get("monthly_goals", []):
                monthly["total"] = total_months
                handler.emit_monthly_generated(monthly)

            # Step 4: Weekly generation (with per-week streaming)
            week_count = 0

            # We need to call weekly_generator which processes all months
            # But we can emit events after getting the result
            for month_idx, monthly in enumerate(state.get("monthly_goals", [])):
                month_num = monthly.get("month_number", month_idx + 1)
                handler.emit_generating_weekly(1, 4, month_num)

            state = await loop.run_in_executor(None, lambda: weekly_gen_node(state))

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

            state = await loop.run_in_executor(None, lambda: daily_gen_node(state))

            # Emit each daily task set
            for monthly_daily in state.get("daily_tasks", []):
                month_num = monthly_daily.get("month_number", 1)
                for week_data in monthly_daily.get("weeks", []):
                    week_num = week_data.get("week_number", 1)
                    daily_tasks = week_data.get("daily_tasks", [])
                    handler.emit_daily_generated(daily_tasks, month_num, week_num)

            # Step 6: Validation
            handler.emit_validating()
            state = await loop.run_in_executor(None, lambda: validator(state))

            # Step 7: Save to DB with fresh session
            handler.emit_saving()

            from app.db.session import SessionLocal
            from app.services.roadmap_service import RoadmapService

            fresh_db = SessionLocal()
            try:
                roadmap_service = RoadmapService(fresh_db)

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
                    user_id=user_id,
                    roadmap_data=roadmap_data,
                    interview_session_id=session_data["id"],
                )

                # Update interview session with roadmap ID
                fresh_service = InterviewService(fresh_db)
                fresh_session = fresh_service.get_session(interview_session_id, user_id)
                if fresh_session:
                    fresh_session.roadmap_id = roadmap.id
                fresh_db.commit()

                await manager.complete(data={
                    "roadmap_id": str(roadmap.id),
                    "title": roadmap.title,
                })
            finally:
                fresh_db.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    # Start generator task immediately (not as background task)
    asyncio.create_task(generate())

    return StreamingResponse(
        manager.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/interviews/batch-answers")
async def submit_batch_answers(
    request: BatchAnswersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit all interview answers at once and refine roadmap.

    This endpoint:
    1. Receives all answers in a batch
    2. Analyzes them to understand user context
    3. Generates roadmap refinements based on all answers
    4. Marks the interview session as ready for roadmap generation
    """
    stream_id = str(uuid.uuid4())
    manager = StreamingManager()
    register_stream(stream_id, manager)

    # Capture values before async task
    user_id = current_user.id
    session_id = request.session_id
    answers = request.answers

    # Get session data in request context
    service = InterviewService(db)
    session = service.get_session(session_id, user_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인터뷰 세션을 찾을 수 없습니다."
        )

    # Capture session info
    session_topic = session.topic
    session_mode = session.mode
    session_duration = session.duration_months
    session_questions = session.current_questions or []

    async def generate():
        try:
            await manager.emit(
                StreamEventType.START,
                "답변을 분석합니다...",
                progress=0
            )

            await manager.emit(
                StreamEventType.PROGRESS,
                "사용자 요구사항 파악 중...",
                progress=10
            )

            # Build context from all answers
            context_lines = []
            for q in session_questions:
                q_id = q.get("id", "")
                q_text = q.get("question", "")
                if q_id in answers:
                    context_lines.append(f"Q: {q_text}")
                    context_lines.append(f"A: {answers[q_id]}")
                    context_lines.append("")

            compiled_context = "\n".join(context_lines)

            await manager.emit(
                StreamEventType.PROGRESS,
                "AI가 로드맵을 구체화하고 있습니다...",
                progress=30
            )

            # Generate refinements based on all answers using AI
            loop = asyncio.get_event_loop()
            refinements = await loop.run_in_executor(
                None,
                lambda: generate_batch_refinements(
                    answers=answers,
                    topic=session_topic,
                    duration_months=session_duration,
                    mode=session_mode,
                    interview_context=compiled_context,
                )
            )

            # Stream each refinement
            total = len(refinements)
            for i, refinement in enumerate(refinements):
                progress = 40 + int((i / max(total, 1)) * 50)

                await manager.emit(
                    StreamEventType.PROGRESS,
                    f"로드맵 업데이트 중... ({i + 1}/{total})",
                    progress=progress,
                    data={"type": "refined", "data": refinement}
                )
                await asyncio.sleep(0.05)

            # Update session with compiled context
            await manager.emit(
                StreamEventType.PROGRESS,
                "저장 중...",
                progress=95
            )

            from app.db.session import SessionLocal
            fresh_db = SessionLocal()
            try:
                fresh_service = InterviewService(fresh_db)
                fresh_session = fresh_service.get_session(session_id, user_id)
                if fresh_session:
                    # Save answers and mark as complete
                    fresh_session.compiled_context = compiled_context
                    fresh_session.status = InterviewStatus.COMPLETED
                    # Convert dict to list of answer objects
                    answer_list = [
                        {"question_id": q_id, "answer": ans}
                        for q_id, ans in answers.items()
                    ]
                    fresh_session.current_answers = answer_list
                    fresh_session.all_answers = answer_list
                    fresh_db.commit()
            finally:
                fresh_db.close()

            await manager.complete(data={
                "session_id": session_id,
                "refinements_applied": total,
                "is_ready_for_generation": True,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            await manager.error(f"오류 발생: {str(e)}")
        finally:
            unregister_stream(stream_id)

    asyncio.create_task(generate())

    return StreamingResponse(
        manager.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


def generate_batch_refinements(
    answers: dict[str, str],
    topic: str,
    duration_months: int,
    mode: str,
    interview_context: str
) -> list:
    """Generate roadmap refinements based on all answers using AI.

    Calls the LLM to generate a complete, personalized roadmap structure
    including title, description, monthly goals, weekly tasks, and daily tasks.
    """
    print(f"[AI Refinement] Generating refinements for topic: {topic}")

    # Build the prompt
    prompt = ROADMAP_REFINEMENT_PROMPT.format(
        topic=topic,
        duration_months=duration_months,
        mode=mode,
        interview_context=interview_context
    )

    try:
        # Call AI to generate the full roadmap structure
        result = invoke_llm(prompt, temperature=0.7)
        print(f"[AI Refinement] AI response received, converting to refinements...")

        # Convert AI response to refinement events
        refinements = convert_roadmap_to_refinements(result, duration_months)
        print(f"[AI Refinement] Generated {len(refinements)} refinement events")

        return refinements

    except Exception as e:
        print(f"[AI Refinement] Error calling AI: {e}")
        # Fallback to basic refinements if AI fails
        return generate_fallback_refinements(topic, duration_months)


def convert_roadmap_to_refinements(roadmap_data: dict, duration_months: int) -> list:
    """Convert AI-generated roadmap structure to refinement events."""
    refinements = []

    # Title refinement
    if "title" in roadmap_data:
        refinements.append({
            "type": "title",
            "value": roadmap_data["title"],
            "path": {}
        })

    # Description refinement
    if "description" in roadmap_data:
        refinements.append({
            "type": "description",
            "value": roadmap_data["description"],
            "path": {}
        })

    # Monthly goals and nested structure
    for monthly in roadmap_data.get("monthly_goals", []):
        month_num = monthly.get("month_number", 1)

        # Monthly title
        if "title" in monthly:
            refinements.append({
                "type": "monthly",
                "field": "title",
                "value": monthly["title"],
                "path": {"month_number": month_num}
            })

        # Monthly description
        if "description" in monthly:
            refinements.append({
                "type": "monthly",
                "field": "description",
                "value": monthly["description"],
                "path": {"month_number": month_num}
            })

        # Weekly tasks
        for weekly in monthly.get("weekly_tasks", []):
            week_num = weekly.get("week_number", 1)

            # Weekly title
            if "title" in weekly:
                refinements.append({
                    "type": "weekly",
                    "field": "title",
                    "value": weekly["title"],
                    "path": {"month_number": month_num, "week_number": week_num}
                })

            # Daily tasks (D1-D7)
            for daily in weekly.get("daily_tasks", []):
                day_num = daily.get("day_number", 1)

                # Daily title
                if "title" in daily:
                    refinements.append({
                        "type": "daily",
                        "field": "title",
                        "value": daily["title"],
                        "path": {
                            "month_number": month_num,
                            "week_number": week_num,
                            "day_number": day_num
                        }
                    })

                # Daily description
                if "description" in daily:
                    refinements.append({
                        "type": "daily",
                        "field": "description",
                        "value": daily["description"],
                        "path": {
                            "month_number": month_num,
                            "week_number": week_num,
                            "day_number": day_num
                        }
                    })

    return refinements


def generate_fallback_refinements(topic: str, duration_months: int) -> list:
    """Generate basic fallback refinements if AI call fails."""
    refinements = []

    refinements.append({
        "type": "title",
        "value": f"{topic} 학습 로드맵",
        "path": {}
    })

    refinements.append({
        "type": "description",
        "value": f"{duration_months}개월 동안 {topic}을(를) 체계적으로 학습합니다.",
        "path": {}
    })

    # Generate basic monthly structure
    for month in range(1, min(duration_months + 1, 4)):
        refinements.append({
            "type": "monthly",
            "field": "title",
            "value": f"{month}개월차: 단계별 학습",
            "path": {"month_number": month}
        })

        # Weekly tasks
        for week in range(1, 5):
            refinements.append({
                "type": "weekly",
                "field": "title",
                "value": f"Week {week}",
                "path": {"month_number": month, "week_number": week}
            })

            # Daily tasks (D1-D7) - only for first month's first week
            if month == 1 and week == 1:
                day_titles = [
                    "기본 개념 학습",
                    "예제 분석",
                    "실습 1",
                    "실습 2",
                    "응용 학습",
                    "주간 복습",
                    "휴식 및 정리"
                ]
                for day in range(1, 8):
                    refinements.append({
                        "type": "daily",
                        "field": "title",
                        "value": f"D{day}: {day_titles[day-1]}",
                        "path": {
                            "month_number": month,
                            "week_number": week,
                            "day_number": day
                        }
                    })

    return refinements


@router.post("/roadmaps/skeleton")
async def generate_roadmap_skeleton(
    request: SkeletonGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate roadmap skeleton (month/week titles only) based on topic and duration.

    This provides the structure of the roadmap before detailed tasks are generated.
    Used to show a preview while the user answers interview questions.
    """
    from app.ai.llm import invoke_llm
    from app.ai.prompts.interview_prompts import (
        SKELETON_GENERATION_PROMPT,
        get_mode_description,
    )

    try:
        prompt = SKELETON_GENERATION_PROMPT.format(
            topic=request.topic,
            mode=request.mode,
            mode_description=get_mode_description(request.mode),
            duration_months=request.duration_months,
        )

        skeleton = invoke_llm(prompt)

        return {
            "success": True,
            "skeleton": skeleton,
            "topic": request.topic,
            "mode": request.mode,
            "duration_months": request.duration_months,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 응답 파싱 실패: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스켈레톤 생성 실패: {str(e)}",
        )


@router.post("/roadmaps/refine")
async def refine_roadmap_on_answer(
    request: RefineOnAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[DEPRECATED] Use /interviews/batch-answers instead.

    This endpoint is deprecated in favor of batch answer submission.
    Individual answer refinement is no longer supported.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="이 엔드포인트는 더 이상 사용되지 않습니다. /interviews/batch-answers를 사용하세요."
    )
