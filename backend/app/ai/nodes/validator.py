from app.ai.state import RoadmapGenerationState


def validator(state: RoadmapGenerationState) -> RoadmapGenerationState:
    """Validate the generated roadmap structure."""
    issues = []

    # Check monthly goals count
    expected_months = state["duration_months"]
    actual_months = len(state.get("monthly_goals", []))
    if actual_months != expected_months:
        issues.append(f"Expected {expected_months} monthly goals, got {actual_months}")

    # Check weekly tasks
    weekly_tasks = state.get("weekly_tasks", [])
    for monthly_data in weekly_tasks:
        month_num = monthly_data.get("month_number")
        weeks = monthly_data.get("weekly_tasks", [])
        if len(weeks) != 4:
            issues.append(f"Month {month_num}: Expected 4 weekly tasks, got {len(weeks)}")

    # Check daily tasks
    daily_tasks = state.get("daily_tasks", [])
    for monthly_data in daily_tasks:
        month_num = monthly_data.get("month_number")
        for week_data in monthly_data.get("weeks", []):
            week_num = week_data.get("week_number")
            days = week_data.get("daily_tasks", [])
            if len(days) != 7:
                issues.append(f"Month {month_num}, Week {week_num}: Expected 7 daily tasks, got {len(days)}")

    if issues:
        state["validation_passed"] = False
        state["error_message"] = "; ".join(issues)
    else:
        state["validation_passed"] = True
        state["error_message"] = None

    return state


def should_retry(state: RoadmapGenerationState) -> str:
    """Determine if we should retry generation or proceed to save."""
    if state.get("validation_passed", False):
        return "save"
    elif state.get("retry_count", 0) < 2:
        return "retry"
    else:
        # Max retries reached, proceed with what we have
        return "save"
