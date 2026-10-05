import re

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage

from app.tools.workout_tool import generate_workout
from app.memory.vector_memory import search_vector_memory
from database.crud import get_user


# ==========================================================
# Workout Planner LLM
# ==========================================================

workout_llm = ChatOllama(
    model="llama3.2",
    temperature=0
).bind_tools([generate_workout])


# ==========================================================
# Helper Functions
# ==========================================================

def has_explicit_focus(text: str) -> bool:
    """
    Check whether the user explicitly mentioned a workout focus.
    """

    text = (text or "").lower()

    focus_terms = [
        "full body",
        "upper body",
        "lower body",
        "chest",
        "back",
        "shoulder",
        "shoulders",
        "biceps",
        "triceps",
        "arms",
        "legs",
        "abs",
        "core",
        "forearms",
    ]

    return any(
        term in text
        for term in focus_terms
    )


def has_explicit_split(text: str) -> bool:
    """
    Check whether the user explicitly mentioned a workout split.
    """

    text = (text or "").lower()

    split_terms = [
        "full body",
        "bro split",
        "push pull legs",
        "push/pull/legs",
        "ppl",
        "upper lower",
        "upper/lower",
        "custom body-part",
    ]

    return any(
        term in text
        for term in split_terms
    )


def extract_focus_from_text(text: str) -> str:
    """
    Extract explicitly requested workout focus.

    Multiple focus areas are returned as a comma-separated string.
    """

    text = (text or "").lower()

    focus_text = text

    # Remove split phrases so that words such as
    # "legs" from "push pull legs" are not treated
    # as an individual focus.
    split_phrases = [
        "push pull legs",
        "push/pull/legs",
        "upper lower",
        "upper/lower",
        "bro split",
        "custom body-part",
    ]

    for phrase in split_phrases:
        focus_text = focus_text.replace(
            phrase,
            ""
        )

    focus_map = {
        "full body": "Full Body",
        "upper body": "Upper Body",
        "lower body": "Lower Body",
        "chest": "Chest",
        "back": "Back",
        "shoulder": "Shoulders",
        "shoulders": "Shoulders",
        "biceps": "Biceps",
        "triceps": "Triceps",
        "arms": "Arms",
        "legs": "Legs",
        "abs": "Abs/Core",
        "core": "Abs/Core",
        "forearms": "Forearms",
    }

    found = []

    for keyword, value in focus_map.items():

        if keyword in focus_text:

            if value not in found:
                found.append(value)

    if not found:
        return "Full Body"

    if "Full Body" in found:
        return "Full Body"

    return ", ".join(found)


def extract_split_from_text(text: str) -> str:
    """
    Extract the explicitly requested workout split.
    """

    text = (text or "").lower()

    if (
        "push pull legs" in text
        or "push/pull/legs" in text
        or "ppl" in text
    ):
        return "Push/Pull/Legs"

    if "bro split" in text:
        return "Bro Split"

    if (
        "upper lower" in text
        or "upper/lower" in text
    ):
        return "Upper/Lower"

    if "custom body-part" in text:
        return "Custom Body-Part"

    if "full body" in text:
        return "Full Body"

    return "Full Body"


def extract_days_from_text(text: str):
    """
    Extract an explicitly requested number of workout days.
    """

    text = (text or "").lower()

    patterns = [
        r"\b([1-7])\s*[- ]?\s*day\b",
        r"\b([1-7])\s*days\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return int(
                match.group(1)
            )

    return None


def extract_equipment_from_text(text: str):
    """
    Extract explicitly requested equipment.
    """

    text = (text or "").lower()

    equipment_map = [
        (
            "resistance bands",
            "Resistance Bands"
        ),
        (
            "resistance band",
            "Resistance Bands"
        ),
        (
            "dumbbells",
            "Dumbbells"
        ),
        (
            "dumbbell",
            "Dumbbells"
        ),
        (
            "barbells",
            "Barbells"
        ),
        (
            "barbell",
            "Barbells"
        ),
        (
            "kettlebells",
            "Kettlebells"
        ),
        (
            "kettlebell",
            "Kettlebells"
        ),
        (
            "no equipment",
            "No Equipment"
        ),
        (
            "without equipment",
            "No Equipment"
        ),
        (
            "bodyweight",
            "No Equipment"
        ),
        (
            "body weight",
            "No Equipment"
        ),
    ]

    for keyword, equipment in equipment_map:

        if keyword in text:
            return equipment

    return None


def extract_goal_from_text(text: str):
    """
    Extract an explicitly requested fitness goal.
    """

    text = (text or "").lower()

    has_weight_loss = (
        "weight loss" in text
        or "lose weight" in text
        or "fat loss" in text
        or "lose fat" in text
    )

    has_weight_gain = (
        "weight gain" in text
        or "gain weight" in text
    )

    has_muscle = (
        "muscle building" in text
        or "build muscle" in text
        or "muscle gain" in text
        or "gain muscle" in text
    )

    if has_weight_loss and has_muscle:
        return "Weight Loss + Muscle Building"

    if has_weight_gain and has_muscle:
        return "Weight Gain + Muscle Building"

    if has_weight_loss:
        return "Weight Loss"

    if has_weight_gain:
        return "Weight Gain"

    if has_muscle:
        return "Muscle Building"

    return None


def extract_difficulty_adjustment(text: str) -> str:
    """
    Detect whether the user wants the workout easier or harder.
    """

    text = (text or "").lower()

    if any(
        word in text
        for word in [
            "easier",
            "less difficult",
            "reduce difficulty",
            "reduce intensity",
            "lighter",
        ]
    ):
        return "easier"

    if any(
        word in text
        for word in [
            "harder",
            "more difficult",
            "increase difficulty",
            "increase intensity",
            "more intense",
        ]
    ):
        return "harder"

    return "normal"


def explicit_cardio_request(text: str) -> bool:
    """
    Detect explicit cardio requests.
    """

    text = (text or "").lower()

    cardio_terms = [
        "cardio",
        "running",
        "jogging",
        "cycling",
        "treadmill",
        "walking",
    ]

    return any(
        word in text
        for word in cardio_terms
    )


# ==========================================================
# Workout Planner Agent
# ==========================================================

def run_workout_planner(user_profile: dict):
    """
    Generate or revise a workout plan.

    For a NEW workout request:
        Current frontend values are used directly.

    For a REVISION:
        Previous structured requirements are preserved unless
        the latest human feedback explicitly changes them.
    """

    user_id = user_profile.get(
        "user_id",
        ""
    )

    user_message = user_profile.get(
        "user_message",
        ""
    )

    approval_feedback = user_profile.get(
        "approval_feedback",
        ""
    )

    reflection = user_profile.get(
        "reflection",
        ""
    )

    previous_requirements = dict(
        user_profile.get(
            "workout_requirements",
            {}
        )
    )

    # ======================================================
    # Get stored user profile
    # ======================================================

    stored_user = (
        get_user(user_id)
        if user_id
        else None
    )

    stored_goal = (
        stored_user.get(
            "goal",
            "General Fitness"
        )
        if stored_user
        else "General Fitness"
    )

    stored_level = (
        stored_user.get(
            "fitness_level",
            "Beginner"
        )
        if stored_user
        else "Beginner"
    )

    # ======================================================
    # Determine whether this is a new request
    # ======================================================

    is_new_request = not bool(
        approval_feedback.strip()
    )

    # ======================================================
    # IMPORTANT EQUIPMENT LOGIC
    #
    # New request:
    #     Frontend equipment wins.
    #
    # Revision:
    #     Previous equipment is preserved unless the user
    #     explicitly changes it in approval feedback.
    # ======================================================

    frontend_equipment = user_profile.get(
        "equipment",
        ""
    )

    frontend_days = user_profile.get(
        "days",
        None
    )

    if is_new_request:

        if frontend_equipment:
            initial_equipment = frontend_equipment
        else:
            initial_equipment = (
                previous_requirements.get(
                    "equipment",
                    "No Equipment"
                )
            )

        if frontend_days is not None:
            initial_days = frontend_days
        else:
            initial_days = (
                previous_requirements.get(
                    "days",
                    3
                )
            )

    else:

        initial_equipment = (
            previous_requirements.get(
                "equipment",
                frontend_equipment
                if frontend_equipment
                else "No Equipment"
            )
        )

        initial_days = (
            previous_requirements.get(
                "days",
                frontend_days
                if frontend_days is not None
                else 3
            )
        )

    # ======================================================
    # Initial Structured Requirements
    # ======================================================

    requirements = {

        "goal": previous_requirements.get(
            "goal",
            stored_goal
        ),

        "level": previous_requirements.get(
            "level",
            stored_level
        ),

        "days": initial_days,

        "equipment": initial_equipment,

        "focus": previous_requirements.get(
            "focus",
            "Full Body"
        ),

        "split": previous_requirements.get(
            "split",
            "Full Body"
        ),

        "difficulty_adjustment": previous_requirements.get(
            "difficulty_adjustment",
            "normal"
        ),

        "cardio_required": previous_requirements.get(
            "cardio_required",
            False
        ),
    }

    # ======================================================
    # Latest Request
    # ======================================================

    if approval_feedback.strip():

        latest_request = (
            approval_feedback.strip()
        )

    else:

        latest_request = (
            user_message.strip()
        )

    # ======================================================
    # Explicit Goal Change
    # ======================================================

    explicit_goal = extract_goal_from_text(
        latest_request
    )

    if explicit_goal:

        requirements["goal"] = (
            explicit_goal
        )

    # ======================================================
    # Explicit Days Change
    # ======================================================

    explicit_days = extract_days_from_text(
        latest_request
    )

    if explicit_days is not None:

        requirements["days"] = (
            explicit_days
        )

    # ======================================================
    # Explicit Equipment Change
    # ======================================================

    explicit_equipment = (
        extract_equipment_from_text(
            latest_request
        )
    )

    if explicit_equipment:

        requirements["equipment"] = (
            explicit_equipment
        )

    # ======================================================
    # Explicit Focus Change
    # ======================================================

    if has_explicit_focus(
        latest_request
    ):

        requirements["focus"] = (
            extract_focus_from_text(
                latest_request
            )
        )

    # ======================================================
    # Explicit Split Change
    # ======================================================

    if has_explicit_split(
        latest_request
    ):

        requirements["split"] = (
            extract_split_from_text(
                latest_request
            )
        )

    # ======================================================
    # Explicit Difficulty Change
    # ======================================================

    difficulty_change = (
        extract_difficulty_adjustment(
            latest_request
        )
    )

    if difficulty_change != "normal":

        requirements[
            "difficulty_adjustment"
        ] = difficulty_change

    # ======================================================
    # Cardio
    # ======================================================

    if explicit_cardio_request(
        latest_request
    ):

        requirements[
            "cardio_required"
        ] = True

    goal_text = str(
        requirements.get(
            "goal",
            ""
        )
    ).lower()

    if "weight loss" in goal_text:

        requirements[
            "cardio_required"
        ] = True

    # ======================================================
    # Long-Term Vector Memory
    # ======================================================

    relevant_memories = []

    try:

        if (
            user_id
            and latest_request.strip()
        ):

            relevant_memories = (
                search_vector_memory(
                    user_id=user_id,
                    query=latest_request,
                    limit=3
                )
            )

    except Exception:

        relevant_memories = []

    memory_text = "\n".join(
        f"- {memory.get('text', '')}"
        for memory in relevant_memories
    )

    if not memory_text:

        memory_text = (
            "No relevant long-term memories found."
        )

    # ======================================================
    # Prompt
    # ======================================================

    prompt = f"""
You are the Workout Planner Agent of the GymFit Agent system.

Generate or revise a workout plan using the structured
requirements provided below.

USER ID:
{user_id}

ORIGINAL USER REQUEST:
{user_message}

LATEST HUMAN FEEDBACK:
{approval_feedback or "None"}

REFLECTION:
{reflection or "None"}

CURRENT STRUCTURED REQUIREMENTS:
{requirements}

RELEVANT LONG-TERM MEMORY:
{memory_text}

==========================================================
REQUIREMENT RULES
==========================================================

1. The latest human feedback has the highest priority
   during a revision.

2. If the latest feedback explicitly changes a requirement,
   use the new value.

3. If the latest feedback does not change a requirement,
   preserve the previous structured value.

4. For a NEW workout request, use the values supplied by
   the frontend.

5. NEVER let an old workout requirement override a new
   frontend equipment selection.

6. NEVER invent a new workout focus.

7. NEVER invent a new workout split.

8. If no focus exists, use Full Body.

9. If no split exists, use Full Body.

10. Preserve workout days during revision unless explicitly
    changed.

11. Preserve equipment during revision unless explicitly
    changed.

12. Preserve the goal unless explicitly changed.

13. Preserve difficulty unless explicitly changed.

14. Preserve cardio once enabled.

15. Weight Loss workouts must include cardio.

16. Use ONLY the specified equipment.

17. Keep the workout suitable for the user's fitness level.

18. Do not provide medical diagnoses or medical treatment.

==========================================================
STRUCTURED REQUIREMENTS
==========================================================

Goal:
{requirements["goal"]}

Fitness Level:
{requirements["level"]}

Days:
{requirements["days"]}

Equipment:
{requirements["equipment"]}

Focus:
{requirements["focus"]}

Split:
{requirements["split"]}

Difficulty:
{requirements["difficulty_adjustment"]}

Cardio Required:
{requirements["cardio_required"]}

==========================================================
TASK
==========================================================

Use the generate_workout tool.

The tool arguments MUST exactly follow the structured
requirements above.

Do not invent different values for:
- goal
- level
- days
- equipment
- focus
- split
- difficulty
- cardio

Return the generated workout plan clearly.
"""

    # ======================================================
    # Ask LLM to call tool
    # ======================================================

    response = workout_llm.invoke(
        prompt
    )

    tool_calls = getattr(
        response,
        "tool_calls",
        []
    )

    # ======================================================
    # Process Tool Call
    # ======================================================

    if tool_calls:

        tool_call = tool_calls[0]

        tool_args = dict(
            tool_call.get(
                "args",
                {}
            )
        )

        # ==================================================
        # FORCE STRUCTURED REQUIREMENTS
        #
        # This prevents the LLM from replacing Dumbbells
        # with No Equipment.
        # ==================================================

        tool_args["goal"] = (
            requirements["goal"]
        )

        tool_args["level"] = (
            requirements["level"]
        )

        tool_args["days"] = (
            requirements["days"]
        )

        tool_args["equipment"] = (
            requirements["equipment"]
        )

        tool_args["focus"] = (
            requirements["focus"]
        )

        tool_args["split"] = (
            requirements["split"]
        )

        tool_args[
            "difficulty_adjustment"
        ] = (
            requirements[
                "difficulty_adjustment"
            ]
        )

        tool_args[
            "cardio_required"
        ] = (
            requirements[
                "cardio_required"
            ]
        )

        # ==================================================
        # DIRECT TOOL INVOCATION
        # ==================================================

        try:

            workout_output = (
                generate_workout.invoke(
                    {
                        "goal":
                            requirements[
                                "goal"
                            ],

                        "level":
                            requirements[
                                "level"
                            ],

                        "days":
                            requirements[
                                "days"
                            ],

                        "equipment":
                            requirements[
                                "equipment"
                            ],

                        "focus":
                            requirements[
                                "focus"
                            ],

                        "split":
                            requirements[
                                "split"
                            ],

                        "difficulty_adjustment":
                            requirements[
                                "difficulty_adjustment"
                            ],

                        "cardio_required":
                            requirements[
                                "cardio_required"
                            ],
                    }
                )
            )

        except Exception as error:

            return {
                "response": AIMessage(
                    content=(
                        "Workout generation failed: "
                        f"{error}"
                    )
                ),

                "workout_requirements":
                    requirements
            }

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        final_response = AIMessage(
            content=str(
                workout_output
            )
        )

        return {
            "response": final_response,

            "workout_requirements":
                dict(requirements)
        }

    # ======================================================
    # FALLBACK
    # ======================================================

    return {
        "response": response,

        "workout_requirements":
            requirements
    }