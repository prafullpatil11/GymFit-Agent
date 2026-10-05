from langgraph.types import Command

from app.graph.fitness_graph import fitness_graph


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_ID = "test_user_003"

config = {
    "configurable": {
        "thread_id": "approval-feedback-test-003"
    }
}


print("\nStarting GymFit Agent...\n")


# ============================================================
# STEP 1: START WORKFLOW
# ============================================================

result = fitness_graph.invoke(
    {
        "user_id": USER_ID,
        "user_message": "Create a workout plan for me.",
        "days": 4,
        "equipment": "Dumbbells"
    },
    config=config
)


print("Workflow interrupted for human approval.\n")


print("First approval request:")
print(result["__interrupt__"])


# ============================================================
# STEP 2: REJECT WITH FEEDBACK
# ============================================================

print("\nHuman decision: REJECT")

print(
    "Feedback: "
    "Make the workout easier and include more cardio.\n"
)


result = fitness_graph.invoke(
    Command(
        resume={
            "status": "reject",
            "feedback": (
                "Make the workout easier and "
                "include more cardio."
            )
        }
    ),
    config=config
)


# ============================================================
# STEP 3: DISPLAY REFLECTION RESULT
# ============================================================

print("\nReflection result:")

print(
    result.get(
        "reflection",
        "No reflection found."
    )
)


# ============================================================
# STEP 4: CHECK SECOND APPROVAL
# ============================================================

if "__interrupt__" in result:

    print(
        "\nWorkout Planner generated a new plan "
        "using the feedback.\n"
    )

    print("Second approval request:")

    print(
        result["__interrupt__"]
    )

else:

    print("\nWorkflow completed.")

    print(
        result.get(
            "final_response",
            "No final response."
        )
    )