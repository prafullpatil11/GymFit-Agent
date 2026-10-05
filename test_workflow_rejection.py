from langgraph.types import Command

from app.graph.fitness_graph import fitness_graph


config = {
    "configurable": {
        "thread_id": "test_workout_rejection_001"
    }
}


# ==========================================================
# STEP 1: Generate Initial Workout Plan
# ==========================================================

result = fitness_graph.invoke(
    {
        "user_id": "test_user_003",
        "user_message": "Create a workout plan for me",
        "days": 3,
        "equipment": "No Equipment"
    },
    config=config
)


print("\n=== INITIAL WORKOUT PLAN ===\n")
print(result["workout_plan"])


print("\n=== FIRST APPROVAL INTERRUPT ===\n")
print(result["__interrupt__"])


# ==========================================================
# STEP 2: Reject Workout + Provide Feedback
# ==========================================================

result = fitness_graph.invoke(
    Command(
        resume={
            "status": "reject",
            "feedback": "Make the workout easier."
        }
    ),
    config=config
)


print("\n=== REVISED WORKOUT PLAN ===\n")
print(result["workout_plan"])


print("\n=== SECOND APPROVAL INTERRUPT ===\n")
print(result["__interrupt__"])


# ==========================================================
# STEP 3: Approve Revised Workout
# ==========================================================

result = fitness_graph.invoke(
    Command(
        resume={
            "status": "approve"
        }
    ),
    config=config
)


print("\n=== FINAL RESPONSE AFTER APPROVAL ===\n")
print(result["final_response"])