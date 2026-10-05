from datetime import datetime


def create_user_document(
    user_id: str,
    name: str,
    age: int,
    weight: float,
    height: float,
    fitness_level: str,
    goal: str
):
    """
    Create a user document for MongoDB.
    """

    return {
        "user_id": user_id,
        "name": name,
        "age": age,
        "weight": weight,
        "height": height,
        "fitness_level": fitness_level,
        "goal": goal,
        "created_at": datetime.now()
    }


def create_workout_document(
    user_id: str,
    workout_name: str,
    duration_minutes: int,
    difficulty: int
):
    """
    Create a workout document for MongoDB.
    """

    return {
        "user_id": user_id,
        "workout_name": workout_name,
        "duration_minutes": duration_minutes,
        "difficulty": difficulty,
        "completed_at": datetime.now()
    }


def create_progress_document(
    user_id: str,
    workouts_completed: int,
    workouts_planned: int,
    average_difficulty: float
):
    """
    Create a progress document for MongoDB.
    """

    return {
        "user_id": user_id,
        "workouts_completed": workouts_completed,
        "workouts_planned": workouts_planned,
        "average_difficulty": average_difficulty,
        "created_at": datetime.now()
    }