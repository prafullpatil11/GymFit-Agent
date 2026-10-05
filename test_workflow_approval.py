from langgraph.types import Command

from app.graph.fitness_graph import fitness_graph


config = {
    "configurable": {
        "thread_id": "test_workout_002"
    }
}


# ---------------------------------------------------------
# Step 1: Start workout workflow
# ---------------------------------------------------------

result = fitness_graph.invoke(
    {
        "user_id": "test_user_003",
        "user_message": "Create a workout plan for me",
        "days": 3,
        "equipment": "No Equipment"
    },
    config=config
)


print("\n=== WORKOUT PLAN GENERATED ===\n")
print(result["workout_plan"])


print("\n=== HUMAN APPROVAL INTERRUPT ===\n")
print(result["__interrupt__"])


# ---------------------------------------------------------
# Step 2: Approve the workout
# ---------------------------------------------------------

result = fitness_graph.invoke(
    Command(
        resume={
            "status": "approve"
        }
    ),
    config=config
)


print("\n=== FINAL RESPONSE ===\n")
print(result["final_response"])