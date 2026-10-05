from database.connection import db


# MongoDB collections
users_collection = db["users"]
workouts_collection = db["workouts"]
progress_collection = db["progress"]


# =========================================================
# USER OPERATIONS
# =========================================================

def save_user(user_document: dict):
    """
    Save a user profile to MongoDB.
    """
    result = users_collection.insert_one(user_document)
    return str(result.inserted_id)


def get_user(user_id: str):
    """
    Retrieve a user profile using user_id.
    """
    return users_collection.find_one(
        {"user_id": user_id}
    )


# =========================================================
# WORKOUT OPERATIONS
# =========================================================

def save_workout(workout_document: dict):
    """
    Save a completed workout to MongoDB.
    """
    result = workouts_collection.insert_one(
        workout_document
    )
    return str(result.inserted_id)


def get_user_workouts(user_id: str):
    """
    Retrieve all workouts belonging to a user.
    """
    return list(
        workouts_collection.find(
            {"user_id": user_id}
        )
    )


def get_workout_progress(user_id: str):
    """
    Calculate basic workout progress from
    stored workout records.
    """

    workouts = list(
        workouts_collection.find(
            {"user_id": user_id}
        )
    )

    workouts_completed = len(workouts)

    # No workout history
    if workouts_completed == 0:
        return {
            "workouts_completed": 0,
            "workouts_planned": 0,
            "average_difficulty": 0
        }

    # Calculate total difficulty
    total_difficulty = sum(
        workout.get("difficulty", 0)
        for workout in workouts
    )

    # Calculate average difficulty
    average_difficulty = (
        total_difficulty / workouts_completed
    )

    return {
        "workouts_completed": workouts_completed,
        "workouts_planned": workouts_completed,
        "average_difficulty": round(
            average_difficulty,
            2
        )
    }


# =========================================================
# PROGRESS OPERATIONS
# =========================================================

def save_progress(progress_document: dict):
    """
    Save workout progress to MongoDB.
    """
    result = progress_collection.insert_one(
        progress_document
    )
    return str(result.inserted_id)


def get_user_progress(user_id: str):
    """
    Retrieve progress records belonging to a user.
    """
    return list(
        progress_collection.find(
            {"user_id": user_id}
        )
    )
def save_or_update_user(user_document: dict):
    """
    Save a new user or update an existing user profile.
    """

    user_id = user_document.get("user_id")

    if not user_id:
        raise ValueError("user_id is required.")

    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": user_document},
        upsert=True
    )

    if result.upserted_id:
        return f"User created: {result.upserted_id}"

    return "User profile updated successfully."