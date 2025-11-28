"""Tests for interview graph workflow."""

import pytest
from unittest.mock import patch, MagicMock

from app.ai.state import DeepInterviewState
from app.ai.interview_graph import (
    start_interview,
    submit_answers,
    serialize_state,
    deserialize_state,
)


class TestInterviewGraphState:
    """Test interview graph state serialization."""

    def test_serialize_state(self):
        """Test serializing interview state."""
        state: DeepInterviewState = {
            "topic": "Python 학습",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {
                "1": [{"id": "q1", "question": "목표?", "question_type": "text"}]
            },
            "answers": {"q1": "웹 개발"},
            "evaluations": {"q1": {"score": 0.8}},
            "stage_data": {"stages": []},
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }

        serialized = serialize_state(state)

        assert isinstance(serialized, dict)
        assert serialized["topic"] == "Python 학습"
        assert serialized["current_stage"] == 1

    def test_deserialize_state(self):
        """Test deserializing interview state."""
        data = {
            "topic": "React",
            "mode": "planning",
            "duration_months": 2,
            "current_stage": 2,
            "stage_name": "현재 상태 파악",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}],
                "2": [{"id": "q2", "question": "Q2", "question_type": "text"}],
            },
            "answers": {"q1": "A1"},
            "evaluations": {"q1": {"score": 0.7}},
            "stage_data": {"stages": []},
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }

        state = deserialize_state(data)

        assert state["topic"] == "React"
        assert state["current_stage"] == 2
        assert "q1" in state["answers"]


class TestStartInterview:
    """Test starting a new interview."""

    @patch("app.ai.interview_graph.create_interview_graph")
    def test_start_interview(self, mock_create_graph):
        """Test starting interview creates initial state."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {
                "1": [
                    {"id": "q1", "question": "목표?", "question_type": "text"},
                    {"id": "q2", "question": "수준?", "question_type": "single_choice", "options": ["초급", "중급"]},
                ]
            },
            "answers": {},
            "evaluations": {},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 2, "answers_count": 0, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }
        mock_create_graph.return_value = mock_graph

        result = start_interview("Python", "learning", 3)

        assert result["topic"] == "Python"
        assert result["current_stage"] == 1
        assert len(result["questions"]["1"]) == 2
        assert result["is_complete"] is False

    @patch("app.ai.interview_graph.create_interview_graph")
    def test_start_interview_initializes_all_stages(self, mock_create_graph):
        """Test that start_interview initializes all 3 stages."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "topic": "React",
            "mode": "planning",
            "duration_months": 2,
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {"1": []},
            "answers": {},
            "evaluations": {},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }
        mock_create_graph.return_value = mock_graph

        result = start_interview("React", "planning", 2)

        assert len(result["stage_data"]["stages"]) == 3


class TestSubmitAnswers:
    """Test submitting answers to interview."""

    @patch("app.ai.interview_graph.create_interview_graph")
    def test_submit_answers_advances_stage(self, mock_create_graph):
        """Test that submitting answers can advance to next stage."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 2,  # Advanced to stage 2
            "stage_name": "현재 상태 파악",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}],
                "2": [{"id": "q2", "question": "Q2", "question_type": "text"}],
            },
            "answers": {"q1": "Answer 1"},
            "evaluations": {"q1": {"score": 0.8, "needs_followup": False}},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 1, "answers_count": 1, "completed": True},
                    {"stage": 2, "questions_count": 1, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }
        mock_create_graph.return_value = mock_graph

        current_state: DeepInterviewState = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}]
            },
            "answers": {},
            "evaluations": {},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 1, "answers_count": 0, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }

        answers = [{"question_id": "q1", "answer": "Answer 1"}]

        result = submit_answers(current_state, answers)

        assert result["current_stage"] == 2
        assert result["stage_data"]["stages"][0]["completed"] is True

    @patch("app.ai.interview_graph.create_interview_graph")
    def test_submit_answers_completes_interview(self, mock_create_graph):
        """Test that submitting final answers completes interview."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 3,
            "stage_name": "제약 조건",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}],
                "2": [{"id": "q2", "question": "Q2", "question_type": "text"}],
                "3": [{"id": "q3", "question": "Q3", "question_type": "text"}],
            },
            "answers": {"q1": "A1", "q2": "A2", "q3": "A3"},
            "evaluations": {
                "q1": {"score": 0.8},
                "q2": {"score": 0.8},
                "q3": {"score": 0.8},
            },
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 1, "answers_count": 1, "completed": True},
                    {"stage": 2, "questions_count": 1, "answers_count": 1, "completed": True},
                    {"stage": 3, "questions_count": 1, "answers_count": 1, "completed": True},
                ]
            },
            "is_complete": True,
            "compiled_context": "User wants to learn Python...",
            "key_insights": ["Beginner level", "2 hours daily"],
            "schedule": {"daily_minutes": 120},
        }
        mock_create_graph.return_value = mock_graph

        current_state: DeepInterviewState = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 3,
            "stage_name": "제약 조건",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}],
                "2": [{"id": "q2", "question": "Q2", "question_type": "text"}],
                "3": [{"id": "q3", "question": "Q3", "question_type": "text"}],
            },
            "answers": {"q1": "A1", "q2": "A2"},
            "evaluations": {"q1": {"score": 0.8}, "q2": {"score": 0.8}},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 1, "answers_count": 1, "completed": True},
                    {"stage": 2, "questions_count": 1, "answers_count": 1, "completed": True},
                    {"stage": 3, "questions_count": 1, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }

        answers = [{"question_id": "q3", "answer": "A3"}]

        result = submit_answers(current_state, answers)

        assert result["is_complete"] is True
        assert result["compiled_context"] != ""
        assert len(result["key_insights"]) > 0


class TestFollowUpLogic:
    """Test follow-up question logic."""

    @patch("app.ai.interview_graph.create_interview_graph")
    def test_low_score_triggers_followup(self, mock_create_graph):
        """Test that low scores trigger follow-up questions."""
        mock_graph = MagicMock()
        # First call: evaluate and generate followup
        mock_graph.invoke.return_value = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 1,  # Still stage 1 due to followup
            "stage_name": "목표 구체화",
            "questions": {
                "1": [
                    {"id": "q1", "question": "Q1", "question_type": "text"},
                    {"id": "q1_followup", "question": "조금 더 구체적으로", "question_type": "text"},
                ]
            },
            "answers": {"q1": "모르겠어요"},  # Vague answer
            "evaluations": {
                "q1": {"score": 0.4, "needs_followup": True, "followup_count": 1}
            },
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 2, "answers_count": 1, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }
        mock_create_graph.return_value = mock_graph

        current_state: DeepInterviewState = {
            "topic": "Python",
            "mode": "learning",
            "duration_months": 3,
            "current_stage": 1,
            "stage_name": "목표 구체화",
            "questions": {
                "1": [{"id": "q1", "question": "Q1", "question_type": "text"}]
            },
            "answers": {},
            "evaluations": {},
            "stage_data": {
                "stages": [
                    {"stage": 1, "questions_count": 1, "answers_count": 0, "completed": False},
                    {"stage": 2, "questions_count": 0, "answers_count": 0, "completed": False},
                    {"stage": 3, "questions_count": 0, "answers_count": 0, "completed": False},
                ]
            },
            "is_complete": False,
            "compiled_context": "",
            "key_insights": [],
            "schedule": {},
        }

        answers = [{"question_id": "q1", "answer": "모르겠어요"}]

        result = submit_answers(current_state, answers)

        # Should still be in stage 1 with follow-up question
        assert result["current_stage"] == 1
        # Should have more questions now (follow-up added)
        assert len(result["questions"]["1"]) > 1
