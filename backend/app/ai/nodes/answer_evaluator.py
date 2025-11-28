"""Answer evaluation node for deep interview system.

Evaluates user answers for specificity, relevance, and completeness.
Generates follow-up questions if answers are too vague.
"""
import json
from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from app.config import settings
from app.ai.state import (
    DeepInterviewState,
    InterviewQuestionData,
    InterviewAnswerData,
    AnswerEvaluationData,
)
from app.ai.prompts.interview_prompts import ANSWER_EVALUATION_PROMPT


# Default threshold for determining if follow-up is needed
DEFAULT_FOLLOWUP_THRESHOLD = 0.6


def create_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3,  # Lower temperature for more consistent evaluation
    )


def _evaluate_single_answer(
    topic: str,
    question: InterviewQuestionData,
    answer: InterviewAnswerData,
    threshold: float = DEFAULT_FOLLOWUP_THRESHOLD,
) -> AnswerEvaluationData:
    """Evaluate a single answer and optionally generate follow-up question."""
    llm = create_llm()

    prompt = ANSWER_EVALUATION_PROMPT.format(
        topic=topic,
        question=question["question"],
        question_type=question["question_type"],
        answer=answer["answer"],
        threshold=threshold,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)

        # Parse follow-up question if present
        followup_question = None
        if result.get("needs_followup") and result.get("followup_question"):
            fq = result["followup_question"]
            followup_question = InterviewQuestionData(
                id=fq.get("id", f"followup_{question['id']}"),
                question=fq.get("question", ""),
                question_type=fq.get("question_type", "text"),
                options=fq.get("options"),
                placeholder=fq.get("placeholder"),
            )

        return AnswerEvaluationData(
            question_id=question["id"],
            specificity=result["scores"]["specificity"],
            relevance=result["scores"]["relevance"],
            completeness=result["scores"]["completeness"],
            average_score=result["average_score"],
            needs_followup=result["needs_followup"],
            followup_question=followup_question,
            insights=result.get("insights", []),
        )

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: assume answer is acceptable if evaluation fails
        return AnswerEvaluationData(
            question_id=question["id"],
            specificity=0.7,
            relevance=0.7,
            completeness=0.7,
            average_score=0.7,
            needs_followup=False,
            followup_question=None,
            insights=[f"Evaluation error: {str(e)}"],
        )


def evaluate_answers(state: DeepInterviewState) -> DeepInterviewState:
    """Evaluate all current answers and determine if follow-ups are needed.

    This node:
    1. Evaluates each answer in current_answers
    2. Generates follow-up questions for vague answers
    3. Updates state with evaluations and pending follow-ups
    """
    topic = state["topic"]
    current_questions = state["current_questions"]
    current_answers = state["current_answers"]

    evaluations: List[AnswerEvaluationData] = []
    pending_followups: List[InterviewQuestionData] = []

    # Create a map of questions by ID for easy lookup
    questions_by_id = {q["id"]: q for q in current_questions}

    for answer in current_answers:
        question = questions_by_id.get(answer["question_id"])
        if not question:
            continue

        evaluation = _evaluate_single_answer(topic, question, answer)
        evaluations.append(evaluation)

        # Collect follow-up questions if needed and not at max followups
        if (
            evaluation["needs_followup"]
            and evaluation["followup_question"]
            and state["followup_count"] < state["max_followups_per_stage"]
        ):
            pending_followups.append(evaluation["followup_question"])

    state["current_evaluations"] = evaluations
    state["pending_followup_questions"] = pending_followups

    return state


def should_probe_deeper(state: DeepInterviewState) -> str:
    """Determine the next step after evaluation.

    Returns:
        - "probe": Need to ask follow-up questions
        - "next_stage": Current stage complete, move to next
        - "complete": All stages complete
    """
    pending_followups = state.get("pending_followup_questions", [])
    current_stage = state["current_stage"]
    followup_count = state.get("followup_count", 0)
    max_followups = state.get("max_followups_per_stage", 2)

    # If there are pending follow-ups and we haven't hit the limit, probe deeper
    if pending_followups and followup_count < max_followups:
        return "probe"

    # Check if all 3 stages are complete
    if current_stage >= 3:
        return "complete"

    # Move to next stage
    return "next_stage"


def format_answers_summary(
    questions: List[InterviewQuestionData],
    answers: List[InterviewAnswerData],
) -> str:
    """Format Q&A into a summary string for next stage prompts."""
    questions_by_id = {q["id"]: q for q in questions}
    summary_parts = []

    for answer in answers:
        question = questions_by_id.get(answer["question_id"])
        if question:
            summary_parts.append(f"Q: {question['question']}\nA: {answer['answer']}")

    return "\n\n".join(summary_parts)
