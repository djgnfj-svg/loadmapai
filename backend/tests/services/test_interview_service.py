"""Tests for interview service."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.interview_session import InterviewSession, InterviewStatus
from app.services.interview_service import InterviewService


@pytest.fixture
def interview_service(db: Session) -> InterviewService:
    """Create interview service instance."""
    return InterviewService(db)


@pytest.fixture
def mock_interview_graph():
    """Mock the interview graph module."""
    with patch("app.services.interview_service.start_interview") as mock_start, \
         patch("app.services.interview_service.submit_answers") as mock_submit:

        mock_start.return_value = {
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {
                "1": [
                    {"id": "q1", "question": "목표는?", "question_type": "text"},
                    {"id": "q2", "question": "수준은?", "question_type": "single_choice", "options": ["초급", "중급"]},
                ]
            },
            "answers": {},
            "evaluations": {},
            "is_complete": False,
        }

        mock_submit.return_value = {
            "current_stage": 2,
            "stage_name": "현재 상태 파악",
            "questions": {
                "1": [{"id": "q1", "question": "목표는?", "question_type": "text"}],
                "2": [{"id": "q3", "question": "현재 수준?", "question_type": "text"}],
            },
            "answers": {"q1": "웹 개발", "q2": "초급"},
            "evaluations": {"q1": {"score": 0.8}, "q2": {"score": 0.9}},
            "is_complete": False,
        }

        yield {"start": mock_start, "submit": mock_submit}


class TestInterviewServiceCreate:
    """Test interview session creation."""

    def test_create_session(
        self, interview_service: InterviewService, test_user: User, mock_interview_graph
    ):
        """Test creating a new interview session."""
        session = interview_service.start_interview(
            user_id=test_user.id,
            topic="Python 학습",
            mode="learning",
            duration_months=3,
        )

        assert session is not None
        assert session.user_id == test_user.id
        assert session.topic == "Python 학습"
        assert session.mode == "learning"
        assert session.duration_months == 3
        assert session.status == InterviewStatus.IN_PROGRESS
        assert session.current_stage == 1

    def test_create_session_initializes_stage_data(
        self, interview_service: InterviewService, test_user: User, mock_interview_graph
    ):
        """Test that creating a session initializes stage data."""
        session = interview_service.start_interview(
            user_id=test_user.id,
            topic="Python",
            mode="learning",
            duration_months=2,
        )

        assert session.stage_data is not None
        assert "stages" in session.stage_data


class TestInterviewServiceGet:
    """Test interview session retrieval."""

    def test_get_session(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test getting a session by ID."""
        # Create session directly
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={"stages": []},
            questions={},
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        retrieved = interview_service.get_session(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.topic == "Test"

    def test_get_session_not_found(self, interview_service: InterviewService):
        """Test getting non-existent session returns None."""
        import uuid
        fake_id = uuid.uuid4()
        result = interview_service.get_session(fake_id)
        assert result is None

    def test_get_user_sessions(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test getting all sessions for a user."""
        # Create multiple sessions
        for i in range(3):
            session = InterviewSession(
                user_id=test_user.id,
                topic=f"Topic {i}",
                mode="learning",
                duration_months=1,
                current_stage=1,
                status=InterviewStatus.IN_PROGRESS,
                stage_data={"stages": []},
                questions={},
                answers={},
                evaluations={},
            )
            db.add(session)
        db.commit()

        sessions, total = interview_service.get_user_sessions(test_user.id)
        assert total == 3
        assert len(sessions) == 3


class TestInterviewServiceQuestions:
    """Test getting current questions."""

    def test_get_current_questions(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test getting current questions for a stage."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={"stages": []},
            questions={
                "1": [
                    {"id": "q1", "question": "Question 1", "question_type": "text"},
                    {"id": "q2", "question": "Question 2", "question_type": "text"},
                ]
            },
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        questions, stage_name = interview_service.get_current_questions(session)
        assert len(questions) == 2
        assert questions[0]["id"] == "q1"

    def test_get_current_questions_completed(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test getting questions for completed session returns empty."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=3,
            status=InterviewStatus.COMPLETED,
            stage_data={"stages": []},
            questions={"3": []},
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        questions, stage_name = interview_service.get_current_questions(session)
        assert len(questions) == 0


class TestInterviewServiceSubmit:
    """Test answer submission."""

    def test_submit_answers(
        self,
        interview_service: InterviewService,
        db: Session,
        test_user: User,
        mock_interview_graph,
    ):
        """Test submitting answers advances the interview."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={
                "stages": [
                    {"stage": 1, "questions_count": 2, "answers_count": 0, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            questions={
                "1": [
                    {"id": "q1", "question": "Q1", "question_type": "text"},
                    {"id": "q2", "question": "Q2", "question_type": "text"},
                ]
            },
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        answers = [
            {"question_id": "q1", "answer": "Answer 1"},
            {"question_id": "q2", "answer": "Answer 2"},
        ]

        updated_session, is_complete, next_questions = interview_service.submit_answers(
            session, answers
        )

        assert updated_session is not None
        assert mock_interview_graph["submit"].called


class TestInterviewServiceAbandon:
    """Test abandoning interviews."""

    def test_abandon_session(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test abandoning an in-progress session."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={"stages": []},
            questions={},
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        result = interview_service.abandon_session(session)
        assert result.status == InterviewStatus.ABANDONED

    def test_abandon_completed_session_fails(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test that abandoning a completed session raises error."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=3,
            status=InterviewStatus.COMPLETED,
            stage_data={"stages": []},
            questions={},
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()

        with pytest.raises(ValueError):
            interview_service.abandon_session(session)


class TestInterviewServiceDelete:
    """Test deleting interviews."""

    def test_delete_session(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test deleting a session."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Test",
            mode="learning",
            duration_months=1,
            current_stage=1,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={"stages": []},
            questions={},
            answers={},
            evaluations={},
        )
        db.add(session)
        db.commit()
        session_id = session.id

        result = interview_service.delete_session(session)
        assert result is True

        # Verify deletion
        deleted = interview_service.get_session(session_id)
        assert deleted is None


class TestSessionToState:
    """Test converting session to graph state."""

    def test_session_to_state(
        self, interview_service: InterviewService, db: Session, test_user: User
    ):
        """Test converting DB session to graph state."""
        session = InterviewSession(
            user_id=test_user.id,
            topic="Python 학습",
            mode="learning",
            duration_months=3,
            current_stage=2,
            status=InterviewStatus.IN_PROGRESS,
            stage_data={
                "stages": [
                    {"stage": 1, "questions_count": 2, "answers_count": 2, "completed": True},
                    {"stage": 2, "questions_count": 2, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            questions={
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}],
                "2": [{"id": "q2", "question": "Q2", "question_type": "text"}],
            },
            answers={"q1": "Answer 1"},
            evaluations={"q1": {"score": 0.8}},
        )
        db.add(session)
        db.commit()

        state = interview_service.session_to_state(session)

        assert state["topic"] == "Python 학습"
        assert state["mode"] == "learning"
        assert state["duration_months"] == 3
        assert state["current_stage"] == 2
        assert "q1" in state["answers"]
