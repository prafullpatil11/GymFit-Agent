from app.memory.long_term_memory import (
    get_user_memory,
    save_user_memory,
    get_workout_history_memory,
    get_progress_memory
)


USER_ID = "test_memory_001"


# ==========================================================
# STEP 1: Save User Profile
# ==========================================================

user_data = {
    "user_id": USER_ID,
    "name": "Memory Test User",
    "age": 21,
    "weight": 75,
    "height": 1.75,
    "fitness_level": "Beginner",
    "goal": "General Fitness"
}

print("\n=== SAVING USER MEMORY ===\n")

save_result = save_user_memory(user_data)

print(save_result)


# ==========================================================
# STEP 2: Retrieve User Profile
# ==========================================================

print("\n=== RETRIEVING USER MEMORY ===\n")

user = get_user_memory(USER_ID)

print(user)


# ==========================================================
# STEP 3: Retrieve Workout History
# ==========================================================

print("\n=== RETRIEVING WORKOUT HISTORY ===\n")

workout_history = get_workout_history_memory(USER_ID)

print("Number of workouts:", len(workout_history))

for workout in workout_history:
    print(workout)


# ==========================================================
# STEP 4: Retrieve Progress
# ==========================================================

print("\n=== RETRIEVING PROGRESS MEMORY ===\n")

progress = get_progress_memory(USER_ID)

print(progress)


# ==========================================================
# STEP 5: Verify
# ==========================================================

print("\n=== LONG-TERM MEMORY CHECK ===\n")

if user and user.get("user_id") == USER_ID:
    print("User profile memory: PASSED")
else:
    print("User profile memory: FAILED")


if isinstance(workout_history, list):
    print("Workout history memory: PASSED")
else:
    print("Workout history memory: FAILED")


if isinstance(progress, dict):
    print("Progress memory: PASSED")
else:
    print("Progress memory: FAILED")