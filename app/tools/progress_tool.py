from langchain_core.tools import tool


@tool
def analyze_progress(
    workouts_completed: int,
    workouts_planned: int,
    average_difficulty: float
) -> str:
    """
    Analyze workout completion and reported difficulty.
    """

    if workouts_planned <= 0:
        return "No planned workouts were provided."

    completion_rate = (
        workouts_completed / workouts_planned
    ) * 100

    completion_rate = round(completion_rate, 2)

    if completion_rate >= 80 and average_difficulty <= 3:
        recommendation = (
            "Progress is consistent. The current workout plan "
            "can be continued."
        )

    elif completion_rate >= 60 and average_difficulty <= 4:
        recommendation = (
            "Progress is moderate. Continue the plan and "
            "monitor workout difficulty."
        )

    else:
        recommendation = (
            "The current plan may need adjustment. "
            "Consider reducing workout difficulty or volume."
        )

    return (
        f"Workout completion rate: {completion_rate}%\n"
        f"Average difficulty: {average_difficulty}/5\n"
        f"Recommendation: {recommendation}"
    )