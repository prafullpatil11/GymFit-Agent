from langchain_ollama import ChatOllama

from app.tools.bmi_tool import calculate_bmi
from app.memory.long_term_memory import get_user_memory


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

assessment_llm = llm.bind_tools(
    [calculate_bmi]
)


def run_assessment(user_profile: dict):
    """
    Fitness Assessment Agent.

    Retrieves the user's stored profile from long-term
    memory and performs a basic fitness assessment.
    """

    user_id = user_profile.get("user_id")

    if not user_id:
        return llm.invoke(
            "User ID is required for fitness assessment."
        )

    # --------------------------------------------------
    # Retrieve user profile from Long-Term Memory
    # --------------------------------------------------

    stored_user = get_user_memory(user_id)

    if not stored_user:
        return llm.invoke(
            f"No user profile was found for user ID: {user_id}."
        )

    # --------------------------------------------------
    # Extract stored profile information
    # --------------------------------------------------

    name = stored_user.get("name", "User")
    age = stored_user.get("age")
    weight = stored_user.get("weight")
    height = stored_user.get("height")
    fitness_level = stored_user.get(
        "fitness_level",
        "Beginner"
    )
    goal = stored_user.get(
        "goal",
        "General Fitness"
    )

    # --------------------------------------------------
    # Assessment Prompt
    # --------------------------------------------------

    prompt = f"""
You are the Fitness Assessment Agent for GymFit Agent.

The following information was retrieved from
long-term memory.

User ID: {user_id}
Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} meters
Fitness Level: {fitness_level}
Goal: {goal}

Your task is to calculate BMI using the BMI tool
when weight and height are available.

IMPORTANT:

Use ONLY the information explicitly provided above
and the BMI value returned by the tool.

Do not interpret the fitness level.

Do not explain what Beginner means.

Do not interpret the fitness goal.

Do not infer exercise experience.

Do not recommend a target weight.

Do not calculate an ideal weight range.

Do not recommend calories or diet.

Do not estimate body-fat percentage.

Do not diagnose medical conditions.

Do not provide medical treatment.

Do not make assumptions about the user.
"""

    response = assessment_llm.invoke(prompt)

    # --------------------------------------------------
    # Execute BMI Tool
    # --------------------------------------------------

    if response.tool_calls:

        for tool_call in response.tool_calls:

            if tool_call["name"] == "calculate_bmi":

                bmi_result = calculate_bmi.invoke(
                    tool_call["args"]
                )

                # --------------------------------------------------
                # Final Assessment
                # --------------------------------------------------

                final_prompt = f"""
You are the Fitness Assessment Agent for GymFit Agent.

Present a concise fitness assessment using ONLY
the information below.

User Profile:

Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} meters
Fitness Level: {fitness_level}
Goal: {goal}

BMI calculated by the BMI tool:

{bmi_result}

Use the following exact information:

Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} meters
Fitness Level: {fitness_level}
Goal: {goal}
BMI: {bmi_result}

IMPORTANT:

1. Do not add interpretations.

2. Do not explain what the fitness level means.

3. Do not explain what the fitness goal means.

4. Do not infer exercise experience.

5. Do not calculate an ideal weight range.

6. Do not provide BMI classification.

7. Do not recommend a target weight.

8. Do not recommend calories or diet.

9. Do not estimate body-fat percentage.

10. Do not diagnose medical conditions.

11. Do not provide medical treatment.

12. Do not add information that is not explicitly
    present above.

Simply present the provided information clearly.
"""

                final_response = llm.invoke(
                    final_prompt
                )

                return final_response

    return response