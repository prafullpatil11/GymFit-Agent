from app.graph.fitness_graph import fitness_graph


config = {
    "configurable": {
        "thread_id": "memory_test_001"
    }
}


# ==========================================================
# FIRST REQUEST
# ==========================================================

result1 = fitness_graph.invoke(
    {
        "user_id": "test_user_003",
        "user_message": "Create a workout plan for me",
        "days": 3,
        "equipment": "No Equipment"
    },
    config=config
)

print("\n=== FIRST REQUEST ===\n")
print("Thread ID: memory_test_001")
print("User ID:", result1.get("user_id"))
print("User Message:", result1.get("user_message"))
print("Workout Plan Generated:", bool(result1.get("workout_plan")))


# ==========================================================
# CHECK SAVED STATE
# ==========================================================

saved_state = fitness_graph.get_state(config)

print("\n=== SAVED SHORT-TERM STATE ===\n")

print("User ID:", saved_state.values.get("user_id"))
print("User Message:", saved_state.values.get("user_message"))
print("Days:", saved_state.values.get("days"))
print("Equipment:", saved_state.values.get("equipment"))
print(
    "Workout Plan Exists:",
    bool(saved_state.values.get("workout_plan"))
)


# ==========================================================
# CHECK SAME THREAD
# ==========================================================

print("\n=== MEMORY CHECK ===\n")

if (
    saved_state.values.get("user_id") == "test_user_003"
    and saved_state.values.get("user_message")
    == "Create a workout plan for me"
):
    print("Short-term memory test: PASSED")
else:
    print("Short-term memory test: FAILED")