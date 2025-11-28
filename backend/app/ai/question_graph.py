from uuid import UUID

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.ai.state import QuestionGenerationState
from app.ai.nodes.topic_analyzer import topic_analyzer
from app.ai.nodes.question_generator import question_generator
from app.ai.nodes.quality_validator import quality_validator, should_retry_question_generation
from app.models import Quiz, Question, DailyTask, WeeklyTask, MonthlyGoal, Roadmap
from app.models.quiz import QuizStatus
from app.models.question import QuestionType


def create_question_graph():
    """Create the LangGraph workflow for quiz question generation."""
    workflow = StateGraph(QuestionGenerationState)

    # Add nodes
    workflow.add_node("topic_analyzer", topic_analyzer)
    workflow.add_node("question_generator", question_generator)
    workflow.add_node("quality_validator", quality_validator)

    # Set entry point
    workflow.set_entry_point("topic_analyzer")

    # Add edges
    workflow.add_edge("topic_analyzer", "question_generator")
    workflow.add_edge("question_generator", "quality_validator")

    # Add conditional edge for retry logic
    workflow.add_conditional_edges(
        "quality_validator",
        should_retry_question_generation,
        {
            "save": END,
            "retry": "question_generator",
        }
    )

    return workflow.compile()


def save_quiz_to_db(state: QuestionGenerationState, db: Session) -> QuestionGenerationState:
    """Save the generated quiz and questions to the database."""
    # Create quiz
    quiz = Quiz(
        daily_task_id=UUID(state["daily_task_id"]),
        user_id=UUID(state["user_id"]),
        status=QuizStatus.PENDING,
        total_questions=len(state["questions"]),
    )
    db.add(quiz)
    db.flush()

    # Create questions
    for i, q_data in enumerate(state["questions"]):
        question_type = QuestionType(q_data["question_type"])

        question = Question(
            quiz_id=quiz.id,
            question_number=i + 1,
            question_type=question_type,
            question_text=q_data["question_text"],
            options=q_data.get("options"),
            correct_answer=q_data.get("correct_answer"),
            explanation=q_data.get("explanation"),
            points=q_data.get("points", 10),
        )
        db.add(question)

    db.commit()
    state["quiz_id"] = str(quiz.id)

    return state


async def generate_quiz(
    daily_task_id: str,
    user_id: str,
    num_questions: int,
    db: Session,
) -> dict:
    """Generate a quiz for a daily task using LangGraph."""
    # Get task hierarchy info
    daily_task = db.query(DailyTask).filter(DailyTask.id == UUID(daily_task_id)).first()
    if not daily_task:
        raise ValueError("Daily task not found")

    weekly_task = db.query(WeeklyTask).filter(WeeklyTask.id == daily_task.weekly_task_id).first()
    if not weekly_task:
        raise ValueError("Weekly task not found")

    monthly_goal = db.query(MonthlyGoal).filter(MonthlyGoal.id == weekly_task.monthly_goal_id).first()
    if not monthly_goal:
        raise ValueError("Monthly goal not found")

    roadmap = db.query(Roadmap).filter(Roadmap.id == monthly_goal.roadmap_id).first()
    if not roadmap:
        raise ValueError("Roadmap not found")

    # Initialize state
    initial_state: QuestionGenerationState = {
        "daily_task_id": daily_task_id,
        "daily_task_title": daily_task.title,
        "daily_task_description": daily_task.description or "",
        "weekly_task_title": weekly_task.title,
        "monthly_goal_title": monthly_goal.title,
        "roadmap_topic": roadmap.topic,
        "num_questions": num_questions,
        "user_id": user_id,
        "key_concepts": [],
        "difficulty_level": "intermediate",
        "question_focus_areas": [],
        "questions": [],
        "validation_passed": False,
        "error_message": None,
        "retry_count": 0,
        "quiz_id": None,
    }

    # Create and run the graph
    graph = create_question_graph()
    final_state = graph.invoke(initial_state)

    # Save to database
    final_state = save_quiz_to_db(final_state, db)

    return {
        "quiz_id": final_state["quiz_id"],
        "total_questions": len(final_state["questions"]),
        "validation_passed": final_state["validation_passed"],
        "error_message": final_state.get("error_message"),
    }
