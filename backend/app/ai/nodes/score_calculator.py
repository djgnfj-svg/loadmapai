from app.ai.state import GradingState


def score_calculator(state: GradingState) -> GradingState:
    """Calculate the total score from grading results."""
    grading_results = state.get("grading_results", [])

    if not grading_results:
        state["total_score"] = 0.0
        state["correct_count"] = 0
        state["total_questions"] = 0
        return state

    # Calculate totals
    total_score = sum(r["score"] for r in grading_results)
    correct_count = sum(1 for r in grading_results if r["is_correct"])
    total_questions = len(grading_results)

    # Normalize score to 0-100 scale
    average_score = total_score / total_questions if total_questions > 0 else 0.0

    state["total_score"] = round(average_score, 1)
    state["correct_count"] = correct_count
    state["total_questions"] = total_questions

    return state
