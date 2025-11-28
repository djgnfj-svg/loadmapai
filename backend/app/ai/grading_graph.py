from uuid import UUID
from typing import List

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.ai.state import GradingState, AnswerData
from app.ai.nodes.answer_analyzer import answer_analyzer
from app.ai.nodes.score_calculator import score_calculator
from app.ai.nodes.feedback_generator import feedback_generator
from app.models import Quiz, Question, UserAnswer, DailyTask
from app.models.quiz import QuizStatus


def create_grading_graph():
    """Create the LangGraph workflow for quiz grading."""
    workflow = StateGraph(GradingState)

    # Add nodes
    workflow.add_node("answer_analyzer", answer_analyzer)
    workflow.add_node("score_calculator", score_calculator)
    workflow.add_node("feedback_generator", feedback_generator)

    # Set entry point
    workflow.set_entry_point("answer_analyzer")

    # Add edges (linear flow)
    workflow.add_edge("answer_analyzer", "score_calculator")
    workflow.add_edge("score_calculator", "feedback_generator")
    workflow.add_edge("feedback_generator", END)

    return workflow.compile()


def save_grading_results(state: GradingState, db: Session) -> GradingState:
    """Save grading results to the database."""
    quiz_id = UUID(state["quiz_id"])

    # Update quiz with results
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz:
        quiz.status = QuizStatus.GRADED
        quiz.score = state["total_score"]
        quiz.correct_count = state["correct_count"]
        quiz.feedback_summary = state["feedback_summary"]

    # Update user answers with grading results
    for result in state["grading_results"]:
        question_id = UUID(result["question_id"])
        user_answer = db.query(UserAnswer).filter(
            UserAnswer.question_id == question_id,
            UserAnswer.user_id == UUID(state["user_id"])
        ).first()

        if user_answer:
            user_answer.is_correct = result["is_correct"]
            user_answer.score = result["score"]
            user_answer.feedback = result["feedback"]

    db.commit()
    return state


async def grade_quiz(
    quiz_id: str,
    user_id: str,
    db: Session,
) -> dict:
    """Grade a completed quiz using LangGraph."""
    # Get quiz and questions
    quiz = db.query(Quiz).filter(Quiz.id == UUID(quiz_id)).first()
    if not quiz:
        raise ValueError("Quiz not found")

    # Get daily task for topic context
    daily_task = db.query(DailyTask).filter(DailyTask.id == quiz.daily_task_id).first()
    topic = daily_task.title if daily_task else "퀴즈"

    questions = db.query(Question).filter(Question.quiz_id == quiz.id).order_by(Question.question_number).all()
    if not questions:
        raise ValueError("No questions found for quiz")

    # Get user answers
    user_answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == UUID(user_id),
        UserAnswer.question_id.in_([q.id for q in questions])
    ).all()

    # Build answer data for grading
    answer_map = {str(ua.question_id): ua for ua in user_answers}
    answers: List[AnswerData] = []

    for q in questions:
        ua = answer_map.get(str(q.id))
        answer_data: AnswerData = {
            "question_id": str(q.id),
            "question_type": q.question_type.value,
            "question_text": q.question_text,
            "correct_answer": q.correct_answer,
            "user_answer": ua.answer_text if ua else "",
            "selected_option": ua.selected_option if ua else None,
            "options": q.options,
        }
        answers.append(answer_data)

    # Initialize state
    initial_state: GradingState = {
        "quiz_id": quiz_id,
        "user_id": user_id,
        "answers": answers,
        "topic": topic,
        "grading_results": [],
        "total_score": 0.0,
        "correct_count": 0,
        "total_questions": len(questions),
        "feedback_summary": "",
        "strengths": [],
        "areas_to_improve": [],
        "current_answer_index": 0,
        "error_message": None,
    }

    # Create and run the graph
    graph = create_grading_graph()
    final_state = graph.invoke(initial_state)

    # Save results to database
    final_state = save_grading_results(final_state, db)

    return {
        "quiz_id": quiz_id,
        "total_score": final_state["total_score"],
        "correct_count": final_state["correct_count"],
        "total_questions": final_state["total_questions"],
        "feedback_summary": final_state["feedback_summary"],
        "strengths": final_state["strengths"],
        "areas_to_improve": final_state["areas_to_improve"],
    }
