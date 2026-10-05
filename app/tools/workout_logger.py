from datetime import datetime

from langchain_core.tools import tool

from database.models import create_workout_document
from database.crud import save_workout


@tool
def log_workout(
    user_id: str,
    workout_name: str,
    duration_minutes: int,
    difficulty: int
) -> str:
    """
    Log a completed workout session and save it to MongoDB.
    """

    if not user_id.strip():
        return "User ID is required."

    if not workout_name.strip():
        return "Workout name is required."

    if duration_minutes <= 0:
        return "Duration must be greater than zero."

    if difficulty < 1 or difficulty > 5:
        return "Difficulty must be between 1 and 5."

    # Create workout document
    workout_document = create_workout_document(
        user_id=user_id,
        workout_name=workout_name,
        duration_minutes=duration_minutes,
        difficulty=difficulty
    )

    # Save workout to MongoDB
    save_workout(workout_document)

    return (
        "Workout logged successfully.\n"
        f"User: {user_id}\n"
        f"Workout: {workout_name}\n"
        f"Duration: {duration_minutes} minutes\n"
        f"Difficulty: {difficulty}/5\n"
        f"Completed at: "
        f"{workout_document['completed_at']}"
    )