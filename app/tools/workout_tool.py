from langchain_core.tools import tool


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_goal(goal: str) -> str:
    """Normalize common goal variations into project-supported goals."""

    text = (goal or "").lower().strip()

    has_loss = any(
        phrase in text
        for phrase in [
            "weight loss",
            "lose weight",
            "fat loss",
            "lose fat",
            "weightloss"
        ]
    )

    has_gain = any(
        phrase in text
        for phrase in [
            "weight gain",
            "gain weight",
            "weightgain"
        ]
    )

    has_muscle = any(
        phrase in text
        for phrase in [
            "muscle building",
            "muscle build",
            "build muscle",
            "muscle gain",
            "muscle growth",
            "build muscles"
        ]
    )

    if has_loss and has_muscle:
        return "Weight Loss + Muscle Building"

    if has_gain and has_muscle:
        return "Weight Gain + Muscle Building"

    if has_loss:
        return "Weight Loss"

    if has_gain:
        return "Weight Gain"

    if has_muscle:
        return "Muscle Building"

    return goal.strip() if goal.strip() else "General Fitness"


def normalize_equipment(equipment: str) -> str:
    """Normalize equipment names."""

    text = (equipment or "").lower().strip()

    if text in [
        "none",
        "no equipment",
        "no equipments",
        "bodyweight",
        "body weight",
        "without equipment"
    ]:
        return "No Equipment"

    if "dumbbell" in text:
        return "Dumbbells"

    if "barbell" in text:
        return "Barbells"

    if (
        "kettlebell" in text
        or "kettle bell" in text
        or "kettle" in text
    ):
        return "Kettlebells"

    if (
        "resistance band" in text
        or "resistance bands" in text
        or "band" in text
    ):
        return "Resistance Bands"

    return "No Equipment"


def normalize_focus(focus: str) -> list:
    """
    Convert natural-language body-part requests into
    a list of supported focus areas.

    Examples:
    Arms + Legs
    Chest and Back
    shoulders, biceps and triceps
    """

    text = (focus or "").lower().strip()

    if not text:
        return ["Full Body"]

    if (
        "full body" in text
        or "full-body" in text
        or text in ["full", "whole body", "whole-body"]
    ):
        return ["Full Body"]

    focus_aliases = {
        "Upper Body": [
            "upper body",
            "upper-body",
            "upper"
        ],
        "Lower Body": [
            "lower body",
            "lower-body"
        ],
        "Chest": [
            "chest",
            "pec",
            "pectorals"
        ],
        "Back": [
            "back",
            "lats"
        ],
        "Shoulders": [
            "shoulder",
            "shoulders",
            "deltoid",
            "delts"
        ],
        "Biceps": [
            "biceps",
            "bicep",
            "bi's"
        ],
        "Triceps": [
            "triceps",
            "tricep"
        ],
        "Arms": [
            "arms",
            "arm",
            "full arm",
            "full arms"
        ],
        "Legs": [
            "legs",
            "leg",
            "leg workout"
        ],
        "Abs/Core": [
            "abs",
            "ab",
            "core",
            "abdominal",
            "abdomen"
        ],
        "Forearms": [
            "forearm",
            "forearms"
        ]
    }

    detected = []

    for focus_name, aliases in focus_aliases.items():

        for alias in aliases:

            if alias in text:

                if focus_name not in detected:
                    detected.append(focus_name)

                break

    if not detected:
        return ["Full Body"]

    # If Arms is explicitly requested, keep Arms.
    # If Biceps + Triceps are requested, they can
    # also be treated as Arms.
    return detected


def normalize_split(split: str) -> str:
    """Normalize workout split."""

    text = (split or "").lower().strip()

    if not text:
        return "Custom Body-Part"

    if (
        "push pull legs" in text
        or "push/pull/legs" in text
        or text == "ppl"
        or "ppl split" in text
    ):
        return "Push/Pull/Legs"

    if (
        "bro split" in text
        or "bro-split" in text
        or "bro" == text
    ):
        return "Bro Split"

    if (
        "upper lower" in text
        or "upper/lower" in text
        or "upper-lower" in text
    ):
        return "Upper/Lower"

    if (
        "full body" in text
        or "full-body" in text
        or text == "full"
    ):
        return "Full Body"

    if (
        "body part" in text
        or "body-part" in text
        or "custom" in text
        or "custom split" in text
    ):
        return "Custom Body-Part"

    return "Custom Body-Part"


def determine_cardio(
    goal: str,
    cardio_required: bool
) -> bool:
    """
    Project rule:

    Weight Loss -> cardio is compulsory.

    Explicit cardio=True also enables cardio.
    """

    normalized_goal = normalize_goal(goal)

    if "Weight Loss" in normalized_goal:
        return True

    return bool(cardio_required)


# ============================================================
# EXERCISE DATABASE
# ============================================================

EXERCISES = {

    "No Equipment": {

        "Full Body": [
            "Bodyweight Squats",
            "Push-ups",
            "Glute Bridges",
            "Mountain Climbers"
        ],

        "Upper Body": [
            "Push-ups",
            "Pike Push-ups",
            "Arm Circles",
            "Superman"
        ],

        "Lower Body": [
            "Bodyweight Squats",
            "Lunges",
            "Glute Bridges",
            "Calf Raises"
        ],

        "Chest": [
            "Push-ups",
            "Wide Push-ups",
            "Incline Push-ups",
            "Knee Push-ups"
        ],

        "Back": [
            "Superman",
            "Bird Dogs",
            "Reverse Snow Angels",
            "Prone Y Raises"
        ],

        "Shoulders": [
            "Pike Push-ups",
            "Arm Circles",
            "Wall Slides",
            "Plank Shoulder Taps"
        ],

        "Biceps": [
            "Isometric Biceps Hold",
            "Towel Curls",
            "Self-Resisted Biceps Curls",
            "Slow Negative Curls"
        ],

        "Triceps": [
            "Diamond Push-ups",
            "Bench Dips",
            "Close-Grip Push-ups",
            "Knee Diamond Push-ups"
        ],

        "Arms": [
            "Diamond Push-ups",
            "Push-ups",
            "Towel Curls",
            "Self-Resisted Biceps Curls"
        ],

        "Legs": [
            "Bodyweight Squats",
            "Reverse Lunges",
            "Glute Bridges",
            "Calf Raises"
        ],

        "Abs/Core": [
            "Plank",
            "Crunches",
            "Leg Raises",
            "Mountain Climbers"
        ],

        "Forearms": [
            "Wrist Circles",
            "Towel Squeeze",
            "Finger Extensions",
            "Wrist Flexion Holds"
        ]
    },

    "Dumbbells": {

        "Full Body": [
            "Dumbbell Goblet Squats",
            "Dumbbell Shoulder Press",
            "One-Arm Dumbbell Rows",
            "Dumbbell Romanian Deadlifts"
        ],

        "Upper Body": [
            "Dumbbell Shoulder Press",
            "Dumbbell Rows",
            "Dumbbell Floor Press",
            "Dumbbell Biceps Curls"
        ],

        "Lower Body": [
            "Dumbbell Goblet Squats",
            "Dumbbell Lunges",
            "Dumbbell Romanian Deadlifts",
            "Dumbbell Calf Raises"
        ],

        "Chest": [
            "Dumbbell Floor Press",
            "Dumbbell Squeeze Press",
            "Dumbbell Fly",
            "Dumbbell Pullover"
        ],

        "Back": [
            "One-Arm Dumbbell Rows",
            "Dumbbell Bent-Over Rows",
            "Dumbbell Reverse Fly",
            "Dumbbell Pullovers"
        ],

        "Shoulders": [
            "Dumbbell Shoulder Press",
            "Dumbbell Lateral Raises",
            "Dumbbell Front Raises",
            "Dumbbell Rear Delt Fly"
        ],

        "Biceps": [
            "Dumbbell Biceps Curls",
            "Dumbbell Hammer Curls",
            "Dumbbell Concentration Curls",
            "Dumbbell Alternating Curls"
        ],

        "Triceps": [
            "Dumbbell Overhead Triceps Extension",
            "Dumbbell Triceps Kickbacks",
            "Dumbbell Close-Grip Press",
            "Dumbbell Tate Press"
        ],

        "Arms": [
            "Dumbbell Biceps Curls",
            "Dumbbell Hammer Curls",
            "Dumbbell Overhead Triceps Extension",
            "Dumbbell Triceps Kickbacks"
        ],

        "Legs": [
            "Dumbbell Goblet Squats",
            "Dumbbell Reverse Lunges",
            "Dumbbell Romanian Deadlifts",
            "Dumbbell Calf Raises"
        ],

        "Abs/Core": [
            "Dumbbell Russian Twists",
            "Dumbbell Dead Bug",
            "Dumbbell Side Bends",
            "Dumbbell Plank Row"
        ],

        "Forearms": [
            "Dumbbell Wrist Curls",
            "Dumbbell Reverse Wrist Curls",
            "Dumbbell Farmer Carry",
            "Dumbbell Holds"
        ]
    },

    "Barbells": {

        "Full Body": [
            "Barbell Squats",
            "Barbell Rows",
            "Barbell Overhead Press",
            "Barbell Romanian Deadlifts"
        ],

        "Upper Body": [
            "Barbell Overhead Press",
            "Barbell Rows",
            "Barbell Close-Grip Press",
            "Barbell Curls"
        ],

        "Lower Body": [
            "Barbell Squats",
            "Barbell Romanian Deadlifts",
            "Barbell Lunges",
            "Barbell Calf Raises"
        ],

        "Chest": [
            "Barbell Bench Press",
            "Barbell Floor Press",
            "Close-Grip Barbell Press",
            "Barbell Pullover"
        ],

        "Back": [
            "Barbell Rows",
            "Barbell Romanian Deadlifts",
            "Barbell Shrugs",
            "Pendlay Rows"
        ],

        "Shoulders": [
            "Barbell Overhead Press",
            "Barbell Front Raises",
            "Barbell Upright Rows",
            "Barbell Shrugs"
        ],

        "Biceps": [
            "Barbell Curls",
            "Close-Grip Barbell Curls",
            "Reverse Barbell Curls",
            "Drag Curls"
        ],

        "Triceps": [
            "Close-Grip Barbell Press",
            "Barbell Skull Crushers",
            "Barbell Floor Press",
            "JM Press"
        ],

        "Arms": [
            "Barbell Curls",
            "Close-Grip Barbell Press",
            "Reverse Barbell Curls",
            "Barbell Skull Crushers"
        ],

        "Legs": [
            "Barbell Squats",
            "Barbell Romanian Deadlifts",
            "Barbell Lunges",
            "Barbell Calf Raises"
        ],

        "Abs/Core": [
            "Barbell Rollouts",
            "Barbell Russian Twists",
            "Barbell Overhead Holds",
            "Barbell Side Bends"
        ],

        "Forearms": [
            "Barbell Wrist Curls",
            "Reverse Barbell Curls",
            "Barbell Holds",
            "Barbell Farmer Holds"
        ]
    },

    "Kettlebells": {

        "Full Body": [
            "Kettlebell Goblet Squats",
            "Kettlebell Swings",
            "Kettlebell Clean and Press",
            "Kettlebell Rows"
        ],

        "Upper Body": [
            "Kettlebell Shoulder Press",
            "Kettlebell Rows",
            "Kettlebell Floor Press",
            "Kettlebell Curls"
        ],

        "Lower Body": [
            "Kettlebell Goblet Squats",
            "Kettlebell Swings",
            "Kettlebell Lunges",
            "Kettlebell Romanian Deadlifts"
        ],

        "Chest": [
            "Kettlebell Floor Press",
            "Kettlebell Crush Press",
            "Kettlebell Pullover",
            "Kettlebell Push-ups"
        ],

        "Back": [
            "Kettlebell Rows",
            "Kettlebell High Pulls",
            "Kettlebell Deadlifts",
            "Kettlebell Pullovers"
        ],

        "Shoulders": [
            "Kettlebell Shoulder Press",
            "Kettlebell Halos",
            "Kettlebell High Pulls",
            "Kettlebell Front Raises"
        ],

        "Biceps": [
            "Kettlebell Curls",
            "Kettlebell Hammer Curls",
            "Kettlebell Concentration Curls",
            "Kettlebell Holds"
        ],

        "Triceps": [
            "Kettlebell Overhead Triceps Extension",
            "Kettlebell Floor Press",
            "Kettlebell Close-Grip Press",
            "Kettlebell Triceps Extension"
        ],

        "Arms": [
            "Kettlebell Curls",
            "Kettlebell Hammer Curls",
            "Kettlebell Overhead Triceps Extension",
            "Kettlebell Close-Grip Press"
        ],

        "Legs": [
            "Kettlebell Goblet Squats",
            "Kettlebell Swings",
            "Kettlebell Lunges",
            "Kettlebell Romanian Deadlifts"
        ],

        "Abs/Core": [
            "Kettlebell Russian Twists",
            "Kettlebell Dead Bug",
            "Kettlebell Windmills",
            "Kettlebell Plank Drag"
        ],

        "Forearms": [
            "Kettlebell Farmer Carry",
            "Kettlebell Holds",
            "Kettlebell Wrist Curls",
            "Kettlebell Bottom-Up Holds"
        ]
    },

    "Resistance Bands": {

        "Full Body": [
            "Resistance Band Squats",
            "Resistance Band Rows",
            "Resistance Band Chest Press",
            "Resistance Band Shoulder Press"
        ],

        "Upper Body": [
            "Resistance Band Chest Press",
            "Resistance Band Rows",
            "Resistance Band Shoulder Press",
            "Resistance Band Biceps Curls"
        ],

        "Lower Body": [
            "Resistance Band Squats",
            "Resistance Band Lunges",
            "Resistance Band Glute Bridges",
            "Resistance Band Calf Raises"
        ],

        "Chest": [
            "Resistance Band Chest Press",
            "Resistance Band Chest Fly",
            "Resistance Band Push-ups",
            "Resistance Band Squeeze Press"
        ],

        "Back": [
            "Resistance Band Rows",
            "Resistance Band Lat Pulldowns",
            "Resistance Band Face Pulls",
            "Resistance Band Straight-Arm Pulldowns"
        ],

        "Shoulders": [
            "Resistance Band Shoulder Press",
            "Resistance Band Lateral Raises",
            "Resistance Band Front Raises",
            "Resistance Band Face Pulls"
        ],

        "Biceps": [
            "Resistance Band Biceps Curls",
            "Resistance Band Hammer Curls",
            "Resistance Band Concentration Curls",
            "Resistance Band Reverse Curls"
        ],

        "Triceps": [
            "Resistance Band Triceps Pushdowns",
            "Resistance Band Overhead Extensions",
            "Resistance Band Kickbacks",
            "Resistance Band Close-Grip Press"
        ],

        "Arms": [
            "Resistance Band Biceps Curls",
            "Resistance Band Hammer Curls",
            "Resistance Band Triceps Pushdowns",
            "Resistance Band Overhead Extensions"
        ],

        "Legs": [
            "Resistance Band Squats",
            "Resistance Band Lunges",
            "Resistance Band Glute Bridges",
            "Resistance Band Calf Raises"
        ],

        "Abs/Core": [
            "Resistance Band Pallof Press",
            "Resistance Band Wood Chops",
            "Resistance Band Dead Bug",
            "Resistance Band Crunches"
        ],

        "Forearms": [
            "Resistance Band Wrist Curls",
            "Resistance Band Reverse Wrist Curls",
            "Resistance Band Holds",
            "Resistance Band Finger Extensions"
        ]
    }
}


# ============================================================
# SPLIT HELPERS
# ============================================================

def build_full_body_split(days: int) -> list:
    return ["Full Body"] * days


def build_ppl_split(days: int) -> list:
    pattern = [
        "Push",
        "Pull",
        "Legs"
    ]

    return [
        pattern[index % len(pattern)]
        for index in range(days)
    ]


def build_upper_lower_split(days: int) -> list:
    pattern = [
        "Upper Body",
        "Lower Body"
    ]

    return [
        pattern[index % len(pattern)]
        for index in range(days)
    ]


def build_bro_split(
    days: int,
    focuses: list
) -> list:
    """
    Distribute body parts across days.

    If fewer focuses than days are supplied,
    the focuses are repeated in rotation.
    """

    usable_focuses = [
        focus
        for focus in focuses
        if focus != "Full Body"
    ]

    if not usable_focuses:
        usable_focuses = ["Full Body"]

    return [
        usable_focuses[index % len(usable_focuses)]
        for index in range(days)
    ]


def build_custom_split(
    days: int,
    focuses: list
) -> list:
    """
    Custom body-part split.

    Multiple requested focuses are distributed
    across the requested days.
    """

    if not focuses:
        focuses = ["Full Body"]

    if focuses == ["Full Body"]:
        return ["Full Body"] * days

    return [
        focuses[index % len(focuses)]
        for index in range(days)
    ]


# ============================================================
# EXERCISE SELECTION
# ============================================================

def get_exercises_for_focus(
    equipment: str,
    focus: str
) -> list:
    """
    Return exercises for a particular equipment
    and focus combination.
    """

    equipment_data = EXERCISES.get(
        equipment,
        EXERCISES["No Equipment"]
    )

    if focus in equipment_data:
        return list(equipment_data[focus])

    # Upper/Lower split support
    if focus == "Upper Body":
        combined = []

        for category in [
            "Chest",
            "Back",
            "Shoulders",
            "Biceps",
            "Triceps"
        ]:
            combined.extend(
                equipment_data.get(category, [])
            )

        return combined[:8]

    if focus == "Lower Body":
        return list(
            equipment_data.get(
                "Legs",
                equipment_data.get(
                    "Lower Body",
                    []
                )
            )
        )

    # Push day
    if focus == "Push":
        combined = []

        for category in [
            "Chest",
            "Shoulders",
            "Triceps"
        ]:
            combined.extend(
                equipment_data.get(category, [])
            )

        return combined

    # Pull day
    if focus == "Pull":
        combined = []

        for category in [
            "Back",
            "Biceps",
            "Forearms"
        ]:
            combined.extend(
                equipment_data.get(category, [])
            )

        return combined

    # Legs day
    if focus == "Legs":
        return list(
            equipment_data.get(
                "Legs",
                equipment_data.get(
                    "Lower Body",
                    equipment_data.get(
                        "Full Body",
                        []
                    )
                )
            )
        )

    return list(
        equipment_data.get(
            "Full Body",
            []
        )
    )


def apply_difficulty(
    exercises: list,
    adjustment: str
) -> list:
    """
    Modify exercise selection based on difficulty.

    This tool changes exercise selection only.
    It does not invent sets or repetitions.
    """

    if not exercises:
        return []

    if adjustment == "easier":

        easier = [
            exercise
            for exercise in exercises
            if not any(
                keyword in exercise.lower()
                for keyword in [
                    "jump",
                    "burpee",
                    "advanced"
                ]
            )
        ]

        if easier:
            return easier[:4]

        return exercises[:3]

    if adjustment == "harder":
        return exercises

    return exercises[:4]


# ============================================================
# WORKOUT TOOL
# ============================================================

@tool
def generate_workout(
    goal: str,
    level: str,
    days: int,
    equipment: str,
    focus: str = "Full Body",
    split: str = "Full Body",
    difficulty_adjustment: str = "normal",
    cardio_required: bool = False
) -> str:
    """
    Generate a structured workout plan.

    Supported:
    - Weight Loss
    - Weight Gain
    - Muscle Building
    - Weight Loss + Muscle Building
    - Weight Gain + Muscle Building

    Supports:
    - 1 to 7 workout days
    - No Equipment
    - Dumbbells
    - Barbells
    - Kettlebells
    - Resistance Bands
    - Multiple body-part focuses
    - Full Body
    - Bro Split
    - Push/Pull/Legs
    - Upper/Lower
    - Custom Body-Part split
    - Normal / Easier / Harder
    - Cardio
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if not isinstance(days, int):
        try:
            days = int(days)
        except (TypeError, ValueError):
            return "Workout days must be a number between 1 and 7."

    if days < 1 or days > 7:
        return "Workout days must be between 1 and 7."

    adjustment = (
        difficulty_adjustment or "normal"
    ).lower().strip()

    if adjustment not in [
        "normal",
        "easier",
        "harder"
    ]:
        adjustment = "normal"

    # ========================================================
    # NORMALIZE INPUTS
    # ========================================================

    normalized_goal = normalize_goal(goal)

    equipment_name = normalize_equipment(
        equipment
    )

    focuses = normalize_focus(
        focus
    )

    split_name = normalize_split(
        split
    )

    # Project cardio rule:
    # Weight Loss always requires cardio.
    final_cardio = determine_cardio(
        normalized_goal,
        cardio_required
    )

    # ========================================================
    # BUILD DAY SPLIT
    # ========================================================

    if split_name == "Full Body":

        day_focuses = build_full_body_split(
            days
        )

    elif split_name == "Push/Pull/Legs":

        day_focuses = build_ppl_split(
            days
        )

    elif split_name == "Upper/Lower":

        day_focuses = build_upper_lower_split(
            days
        )

    elif split_name == "Bro Split":

        day_focuses = build_bro_split(
            days,
            focuses
        )

    else:

        day_focuses = build_custom_split(
            days,
            focuses
        )

    # ========================================================
    # HEADER
    # ========================================================

    plan = f"""
Workout Plan

Fitness Goal: {normalized_goal}
Fitness Level: {level}
Workout Days: {days}
Equipment: {equipment_name}
Workout Focus: {", ".join(focuses)}
Workout Split: {split_name}
Difficulty Adjustment: {adjustment}
Cardio Required: {final_cardio}

Suggested Weekly Plan:
"""

    # ========================================================
    # GENERATE EACH DAY
    # ========================================================

    for day_index in range(days):

        current_focus = day_focuses[
            day_index
        ]

        selected_exercises = get_exercises_for_focus(
            equipment_name,
            current_focus
        )

        # For custom body-part plans, if a focus is
        # not directly available, use its exercise group.
        if not selected_exercises:

            selected_exercises = get_exercises_for_focus(
                equipment_name,
                focuses[
                    day_index % len(focuses)
                ]
            )

        exercise_pool = apply_difficulty(
            selected_exercises,
            adjustment
        )

        # Rotate exercises between days so that
        # repeated focuses do not always show
        # exactly the same first exercises.
        if exercise_pool:

            rotation = (
                day_index
                % len(exercise_pool)
            )

            exercise_pool = (
                exercise_pool[rotation:]
                + exercise_pool[:rotation]
            )

        day_exercises = exercise_pool[:4]

        # If fewer than 4 are available,
        # use whatever is available.
        day_exercises = list(
            dict.fromkeys(day_exercises)
        )

        plan += f"""

Day {day_index + 1}: {current_focus}
"""

        for exercise in day_exercises:
            plan += f"- {exercise}\n"

    # ========================================================
    # CARDIO
    # ========================================================

    if final_cardio:

        if adjustment == "easier":

            plan += """
Cardio:

- Light Walking
- Standing Marching
"""

        elif adjustment == "harder":

            plan += """
Cardio:

- Brisk Walking
- Jogging
"""

        else:

            plan += """
Cardio:

- Brisk Walking
- Cycling
"""

    # ========================================================
    # RETURN
    # ========================================================

    return plan