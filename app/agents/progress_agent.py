from langchain_ollama import ChatOllama

from app.tools.progress_tool import analyze_progress
from database.crud import get_workout_progress


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


def run_progress_analysis(progress_data: dict):
    """
    Progress Analyst Agent.

    Retrieves workout progress from MongoDB and
    analyzes the stored workout history.
    """

    user_id = progress_data.get("user_id", "")

    if not user_id:
        return llm.invoke(
            "User ID is required to analyze workout progress."
        )

    # Retrieve progress from MongoDB
    progress = get_workout_progress(user_id)

    workouts_completed = progress.get(
        "workouts_completed",
        0
    )

    workouts_planned = progress.get(
        "workouts_planned",
        0
    )

    average_difficulty = progress.get(
        "average_difficulty",
        0
    )

    # Analyze progress using the existing tool
    progress_result = analyze_progress.invoke(
        {
            "workouts_completed": workouts_completed,
            "workouts_planned": workouts_planned,
            "average_difficulty": float(
                average_difficulty
            )
        }
    )

    prompt = f"""
You are the Progress Analyst Agent for GymFit Agent.

The workout history was retrieved from MongoDB.

MongoDB Progress Data:
{progress}

The progress analysis tool produced:

{progress_result}

Present the result clearly.

Include:
- Workout completion rate
- Average difficulty
- Recommendation

IMPORTANT:
- Use ONLY the information provided above.
- Do not invent additional statistics.
- Do not create a new workout plan.
- Do not change the tool's recommendation.
- Do not diagnose medical conditions.
- Do not provide medical treatment.
"""

    response = llm.invoke(prompt)

    return response