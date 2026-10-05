from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


def run_supervisor(user_message: str):
    """
    Decide which specialist agent should handle
    the user's request.
    """

    prompt = f"""
You are the Supervisor Agent for FitAgent.

Analyze the user's request:

{user_message}

Available specialist agents:

1. Assessment Agent
   - Handles fitness profiles and BMI calculation.

2. Workout Planner Agent
   - Creates workout plans.

3. Progress Analyst Agent
   - Analyzes workout progress.

4. Fitness Coach Agent
   - Handles general fitness questions and
     final responses.

IMPORTANT:
Return ONLY ONE of the following exact names:

Assessment Agent
Workout Planner Agent
Progress Analyst Agent
Fitness Coach Agent

Do not provide an explanation.
Do not provide a sentence.
Do not use markdown.
Return only the agent name.
"""

    response = llm.invoke(prompt)

    return response