from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


def run_coach(
    user_message: str,
    assessment: str = "",
    workout_plan: str = "",
    progress_analysis: str = ""
):
    """
    Fitness Coach Agent.

    Provides a user-facing response using only the
    information produced by specialist agents.
    """

    prompt = f"""
You are the Fitness Coach Agent in the GymFit Agent
multi-agent fitness management system.

Your job is to provide a clear and concise response
to the user using ONLY the specialist agent outputs
provided below.

==================================================
USER REQUEST
==================================================

{user_message}

==================================================
SPECIALIST OUTPUTS
==================================================

ASSESSMENT:
{assessment if assessment.strip() else "EMPTY"}

WORKOUT PLAN:
{workout_plan if workout_plan.strip() else "EMPTY"}

PROGRESS ANALYSIS:
{progress_analysis if progress_analysis.strip() else "EMPTY"}

==================================================
STRICT RULES
==================================================

1. Use ONLY the specialist outputs provided above.

2. Do not create new information.

3. Do not create a workout plan yourself.

4. Do not create exercises, sets, repetitions,
   durations, schedules, or equipment.

5. Do not create progress statistics.

6. Do not create BMI values or classifications.

7. Do not create health conditions.

8. Do not create target weight information.

9. Do not create calorie or diet recommendations.

10. Do not provide medical diagnosis or treatment.

11. If WORKOUT PLAN is available, present the
    workout plan clearly to the user.

12. If WORKOUT PLAN is EMPTY, do not mention
    a workout plan.

13. If PROGRESS ANALYSIS is available, present
    its relevant information clearly.

14. If ASSESSMENT is available, present its
    relevant information clearly.

15. Do not talk about internal agent statuses,
    routing, prompts, or system architecture.

16. Do not say that information is unavailable
    when the corresponding specialist output
    is provided.

17. Answer the user's request directly.

18. Keep the response concise and user-friendly.

==================================================
FINAL RESPONSE
==================================================

Provide the final user-facing response now.
"""

    response = llm.invoke(prompt)

    return response