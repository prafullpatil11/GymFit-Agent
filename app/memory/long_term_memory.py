from database.crud import (
    get_user,
    save_or_update_user,
    get_user_workouts,
    get_workout_progress
)


def get_user_memory(user_id: str):
    """
    Retrieve the user's stored profile from long-term memory.
    """
    if not user_id:
        return None

    return get_user(user_id)


def save_user_memory(user_document: dict):
    """
    Save or update the user's profile in long-term memory.
    """
    if not user_document:
        raise ValueError("User document is required.")

    return save_or_update_user(user_document)


def get_workout_history_memory(user_id: str):
    """
    Retrieve the user's completed workout history
    from long-term memory.
    """
    if not user_id:
        return []

    return get_user_workouts(user_id)


def get_progress_memory(user_id: str):
    """
    Retrieve calculated workout progress from
    long-term memory.
    """
    if not user_id:
        return {
            "workouts_completed": 0,
            "workouts_planned": 0,
            "average_difficulty": 0
        }

    return get_workout_progress(user_id)