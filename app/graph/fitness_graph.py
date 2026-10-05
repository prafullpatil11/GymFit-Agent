from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama

from app.agents.supervisor_agent import run_supervisor
from app.agents.assessment_agent import run_assessment
from app.agents.workout_agent import run_workout_planner
from app.agents.progress_agent import run_progress_analysis
from app.agents.coach_agent import run_coach


# ==========================================================
# Reflection LLM
# ==========================================================

reflection_llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


# ==========================================================
# Fitness Graph State
# ==========================================================

class FitnessState(TypedDict, total=False):

    # ------------------------------------------------------
    # Basic user request
    # ------------------------------------------------------

    user_message: str
    user_id: str

    # ------------------------------------------------------
    # Basic workout inputs
    # ------------------------------------------------------

    days: int
    equipment: str

    # ------------------------------------------------------
    # Structured workout requirements
    # ------------------------------------------------------

    workout_requirements: dict

    # ------------------------------------------------------
    # Other application state
    # ------------------------------------------------------

    user_profile: dict
    progress_data: dict

    assessment: str
    workout_plan: str
    progress_analysis: str

    supervisor_decision: str

    # ------------------------------------------------------
    # Human Approval
    # ------------------------------------------------------

    approval_status: str
    approval_feedback: str

    # ------------------------------------------------------
    # Reflection
    # ------------------------------------------------------

    reflection: str

    # ------------------------------------------------------
    # Final response
    # ------------------------------------------------------

    final_response: str


# ==========================================================
# Supervisor Node
# ==========================================================

def supervisor_node(state):

    response = run_supervisor(
        state["user_message"]
    )

    return {
        "supervisor_decision": response.content.strip()
    }


# ==========================================================
# Assessment Node
# ==========================================================

def assessment_node(state):

    response = run_assessment(
        {
            "user_id": state["user_id"]
        }
    )

    return {
        "assessment": response.content
    }


# ==========================================================
# Workout Planner Node
# ==========================================================

def workout_node(state):

    # ------------------------------------------------------
    # Existing structured workout requirements
    # ------------------------------------------------------

    workout_requirements = dict(
        state.get(
            "workout_requirements",
            {}
        )
    )

    # ------------------------------------------------------
    # Build user profile for Workout Planner
    # ------------------------------------------------------

    user_profile = {
        "user_id": state["user_id"],

        "user_message": state.get(
            "user_message",
            ""
        ),

        "days": state.get(
            "days",
            workout_requirements.get(
                "days",
                3
            )
        ),

        "equipment": state.get(
            "equipment",
            workout_requirements.get(
                "equipment",
                "No Equipment"
            )
        ),

        # --------------------------------------------------
        # IMPORTANT:
        # Pass the complete structured requirements
        # from the previous iteration.
        # --------------------------------------------------

        "workout_requirements": workout_requirements
    }

    # ------------------------------------------------------
    # Human Approval feedback
    # ------------------------------------------------------

    feedback = state.get(
        "approval_feedback",
        ""
    )

    if feedback:

        user_profile[
            "approval_feedback"
        ] = feedback

    # ------------------------------------------------------
    # Reflection
    # ------------------------------------------------------

    reflection = state.get(
        "reflection",
        ""
    )

    if reflection:

        user_profile[
            "reflection"
        ] = reflection

    # ------------------------------------------------------
    # Generate workout
    # ------------------------------------------------------

    response = run_workout_planner(
        user_profile
    )

    # ------------------------------------------------------
    # New Workout Planner format
    #
    # The updated Workout Planner will return:
    #
    # {
    #     "response": AIMessage,
    #     "workout_requirements": {...}
    # }
    #
    # Keep compatibility with the previous format too.
    # ------------------------------------------------------

    if isinstance(response, dict):

        workout_response = response.get(
            "response"
        )

        updated_requirements = response.get(
            "workout_requirements",
            workout_requirements
        )

        if workout_response is None:

            workout_response = response

        workout_content = getattr(
            workout_response,
            "content",
            str(workout_response)
        )

        return {
            "workout_plan": workout_content,

            "workout_requirements":
                updated_requirements,

            "final_response": ""
        }

    # ------------------------------------------------------
    # Backward-compatible fallback
    # ------------------------------------------------------

    return {
        "workout_plan": response.content,

        "workout_requirements":
            workout_requirements,

        "final_response": ""
    }


# ==========================================================
# Human Approval Node
# ==========================================================

def human_approval_node(state):

    workout_plan = state.get(
        "workout_plan",
        ""
    )

    approval = interrupt(
        {
            "type": "workout_approval",

            "message":
                "Please review the proposed workout plan.",

            "workout_plan":
                workout_plan,

            "options": [
                "approve",
                "reject"
            ],

            "feedback_required_for_rejection":
                True
        }
    )

    # ------------------------------------------------------
    # Process approval response
    # ------------------------------------------------------

    if isinstance(approval, dict):

        status = str(
            approval.get(
                "status",
                ""
            )
        ).lower()

        feedback = str(
            approval.get(
                "feedback",
                ""
            )
        )

        return {
            "approval_status": status,

            "approval_feedback":
                feedback
        }

    return {
        "approval_status":
            str(approval).lower()
    }


# ==========================================================
# Reflection Node
# ==========================================================

def reflection_node(state):

    feedback = state.get(
        "approval_feedback",
        ""
    )

    previous_workout = state.get(
        "workout_plan",
        ""
    )

    # ------------------------------------------------------
    # Current structured requirements
    # ------------------------------------------------------

    current_requirements = state.get(
        "workout_requirements",
        {}
    )

    prompt = f"""
You are the Reflection component of the GymFit Agent.

The human reviewed and rejected the previously
generated workout plan.

========================================================
PREVIOUS WORKOUT
========================================================

{previous_workout}

========================================================
CURRENT STRUCTURED REQUIREMENTS
========================================================

{current_requirements}

========================================================
HUMAN FEEDBACK
========================================================

{feedback}

========================================================
TASK
========================================================

Accurately interpret what the human wants changed
in the next workout.

The Workout Planner will use the structured
requirements separately.

Return a short reflection containing:

1. What the user wants changed.
2. What should be adjusted in the next workout.
3. Any specific requirement explicitly stated
   by the user.

IMPORTANT:

- Treat human feedback as the source of truth.
- Preserve the exact meaning of the user's request.
- Do not reverse or contradict the feedback.
- Do not create a workout plan.
- Do not create exercises.
- Do not create sets or repetitions.
- Do not provide medical advice.
- Do not provide diet or calorie recommendations.
- Do not invent user preferences.
- Do not change the user's request.
- Do not create new requirements that are not
  explicitly stated.
- Do not treat examples as requirements.
- Keep the reflection concise.

Reflection:
"""

    response = reflection_llm.invoke(
        prompt
    )

    return {
        "reflection":
            response.content.strip()
    }


# ==========================================================
# Progress Analysis Node
# ==========================================================

def progress_node(state):

    response = run_progress_analysis(
        {
            "user_id": state["user_id"]
        }
    )

    progress_output = getattr(
        response,
        "content",
        str(response)
    )

    return {
        "progress_analysis":
            progress_output
    }


# ==========================================================
# Fitness Coach Node
# ==========================================================

def coach_node(state):

    response = run_coach(
        user_message=state["user_message"],

        assessment=state.get(
            "assessment",
            ""
        ),

        workout_plan=state.get(
            "workout_plan",
            ""
        ),

        progress_analysis=state.get(
            "progress_analysis",
            ""
        )
    )

    return {
        "final_response":
            response.content
    }


# ==========================================================
# Supervisor Routing
# ==========================================================

def route_from_supervisor(state):

    decision = state.get(
        "supervisor_decision",
        ""
    ).lower()

    if "progress analyst agent" in decision:
        return "progress"

    if "workout planner agent" in decision:
        return "workout"

    if "assessment agent" in decision:
        return "assessment"

    return "coach"


# ==========================================================
# Human Approval Routing
# ==========================================================

def route_after_approval(state):

    approval = state.get(
        "approval_status",
        ""
    ).lower()

    # ------------------------------------------------------
    # Approved
    # ------------------------------------------------------

    if approval in [
        "approve",
        "approved"
    ]:

        return "coach"

    # ------------------------------------------------------
    # Rejected
    # ------------------------------------------------------

    if approval == "reject":

        return "reflection"

    # ------------------------------------------------------
    # Default
    # ------------------------------------------------------

    return "reflection"


# ==========================================================
# Build LangGraph
# ==========================================================

builder = StateGraph(
    FitnessState
)


# ==========================================================
# Add Nodes
# ==========================================================

builder.add_node(
    "supervisor",
    supervisor_node
)

builder.add_node(
    "assessment",
    assessment_node
)

builder.add_node(
    "workout",
    workout_node
)

builder.add_node(
    "human_approval",
    human_approval_node
)

builder.add_node(
    "reflection",
    reflection_node
)

builder.add_node(
    "progress",
    progress_node
)

builder.add_node(
    "coach",
    coach_node
)


# ==========================================================
# Starting Point
# ==========================================================

builder.add_edge(
    START,
    "supervisor"
)


# ==========================================================
# Supervisor Conditional Routing
# ==========================================================

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "assessment": "assessment",
        "workout": "workout",
        "progress": "progress",
        "coach": "coach"
    }
)


# ==========================================================
# Assessment → Coach
# ==========================================================

builder.add_edge(
    "assessment",
    "coach"
)


# ==========================================================
# Workout → Human Approval
# ==========================================================

builder.add_edge(
    "workout",
    "human_approval"
)


# ==========================================================
# Human Approval Routing
# ==========================================================

builder.add_conditional_edges(
    "human_approval",
    route_after_approval,
    {
        "coach": "coach",
        "reflection": "reflection"
    }
)


# ==========================================================
# Reflection → Workout Planner
# ==========================================================

builder.add_edge(
    "reflection",
    "workout"
)


# ==========================================================
# Progress → Coach
# ==========================================================

builder.add_edge(
    "progress",
    "coach"
)


# ==========================================================
# Coach → End
# ==========================================================

builder.add_edge(
    "coach",
    END
)


# ==========================================================
# Short-Term Checkpoint Memory
# ==========================================================

checkpointer = MemorySaver()


# ==========================================================
# Compile Fitness Graph
# ==========================================================

fitness_graph = builder.compile(
    checkpointer=checkpointer
)