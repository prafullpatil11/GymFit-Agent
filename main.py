from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langgraph.types import Command
from app.agents.progress_agent import run_progress_analysis
from app.graph.fitness_graph import fitness_graph
from database.crud import save_or_update_user, get_user, get_user_workouts


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="GymFit Agent API",
    description="Agentic AI-based Fitness and Workout Management System",
    version="1.0.0"
)


# ==========================================================
# CORS Configuration
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Request Models
# ==========================================================

class WorkoutRequest(BaseModel):
    user_id: str
    user_message: str
    days: int = 3
    equipment: str = "No Equipment"


class ApprovalRequest(BaseModel):
    user_id: str
    status: str
    feedback: str = ""


class AssessmentRequest(BaseModel):
    user_id: str


class ProgressRequest(BaseModel):
    user_id: str


class LogWorkoutRequest(BaseModel):
    user_id: str
    workout_name: str
    duration_minutes: int
    difficulty: int


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
def root():
    return {
        "message": "GymFit Agent API is running"
    }


# ==========================================================
# Health Endpoint
# ==========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ==========================================================
# Workout Endpoint
# ==========================================================
# ==========================================================
# Workout Endpoint
# ==========================================================

@app.post("/workout")
def create_workout(request: WorkoutRequest):

    config = {
        "configurable": {
            "thread_id": f"api_{request.user_id}"
        }
    }

    # ------------------------------------------------------
    # Start a completely NEW workout request
    # ------------------------------------------------------
    #
    # This prevents LangGraph checkpoint memory from
    # reusing requirements from the previous workout.
    #
    # Example:
    #
    # Previous:
    # 3 Days + Kettlebells
    #
    # New request:
    # 6 Days + Resistance Band
    #
    # The new request must start fresh.
    # ------------------------------------------------------

    result = fitness_graph.invoke(
        {
            "user_id": request.user_id,
            "user_message": request.user_message,
            "days": request.days,
            "equipment": request.equipment,

            "new_workout_request": True
        },
        config=config
    )

    return {
        "status": "success",
        "user_id": request.user_id,

        "workout_plan": result.get(
            "workout_plan",
            ""
        ),

        "approval_required": "__interrupt__" in result,

        "interrupt": str(
            result.get(
                "__interrupt__",
                ""
            )
        )
    }
# ==========================================================
# Workout Approval Endpoint
# ==========================================================

@app.post("/workout/approval")
def workout_approval(request: ApprovalRequest):

    config = {
        "configurable": {
            "thread_id": f"api_{request.user_id}"
        }
    }

    result = fitness_graph.invoke(
        Command(
            resume={
                "status": request.status,
                "feedback": request.feedback
            }
        ),
        config=config
    )

    return {
        "status": "success",
        "user_id": request.user_id,
        "approval_status": request.status,
        "feedback": request.feedback,
        "workout_plan": result.get(
            "workout_plan",
            ""
        ),
        "approval_required": "__interrupt__" in result,
        "final_response": result.get(
            "final_response",
            ""
        )
    }


# ==========================================================
# USER PROFILE ENDPOINTS
# ==========================================================

@app.post("/users")
def create_user(user_document: dict):
    """Create or update a user profile."""
    result = save_or_update_user(user_document)
    return {
        "status": result
    }


@app.get("/users/{user_id}")
def get_user_profile(user_id: str):
    """Retrieve a user profile by user_id."""

    user = get_user(user_id)

    if not user:
        return {
            "error": "User not found"
        }, 404

    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user.get("_id", ""))

    return user


# ==========================================================
# ASSESSMENT ENDPOINT
# ==========================================================

from app.agents.assessment_agent import run_assessment


@app.post("/assessment")
def get_fitness_assessment(request: AssessmentRequest):
    """Run fitness assessment using Assessment Agent."""

    user = get_user(request.user_id)

    if not user:
        return {
            "error": (
                f"No user profile was found for user ID: "
                f"{request.user_id}."
            )
        }, 404

    res = run_assessment({
        "user_id": request.user_id
    })

    content = getattr(
        res,
        "content",
        str(res)
    )

    return {
        "status": "success",
        "user_id": request.user_id,
        "profile": {
            "name": user.get("name", "User"),
            "age": user.get("age"),
            "weight": user.get("weight"),
            "height": user.get("height"),
            "fitness_level": user.get(
                "fitness_level",
                "Beginner"
            ),
            "goal": user.get(
                "goal",
                "General Fitness"
            )
        },
        "assessment_result": content
    }


# ==========================================================
# WORKOUT LOGGING ENDPOINT
# ==========================================================

from app.tools.workout_logger import log_workout


@app.post("/workout/log")
def log_completed_workout(
    request: LogWorkoutRequest
):
    """
    Log a completed workout session using
    log_workout tool with validation.
    """

    # Basic validation
    if not request.user_id.strip():
        return {
            "status": "error",
            "message": "User ID is required."
        }

    if not request.workout_name.strip():
        return {
            "status": "error",
            "message": "Workout name is required."
        }

    if request.duration_minutes <= 0:
        return {
            "status": "error",
            "message": "Duration must be greater than zero."
        }

    if request.difficulty < 1 or request.difficulty > 5:
        return {
            "status": "error",
            "message": "Difficulty must be between 1 and 5."
        }

    # Invoke the logging tool
    log_workout.invoke({
        "user_id": request.user_id,
        "workout_name": request.workout_name,
        "duration_minutes": request.duration_minutes,
        "difficulty": request.difficulty
    })

    return {
        "status": "success",
        "message": "Workout logged successfully."
    }


# ==========================================================
# PROGRESS ANALYSIS ENDPOINT
# ==========================================================

@app.post("/progress/analyze")
def analyze_progress_endpoint(
    request: ProgressRequest
):
    """Analyze user progress using the Progress Analyst Agent."""

    if not request.user_id.strip():
        return {
            "status": "error",
            "message": "User ID is required for progress analysis."
        }

    result = run_progress_analysis({
        "user_id": request.user_id
    })

    content = getattr(
        result,
        "content",
        str(result)
    )

    return {
        "status": "success",
        "message": content
    }


# ==========================================================
# USER WORKOUT HISTORY ENDPOINT
# ==========================================================

@app.get("/users/{user_id}/workouts")
def get_user_workout_history(
    user_id: str
):
    """Retrieve workout history for a user, sorted newest first."""

    if not user_id or not user_id.strip():
        return {
            "user_id": user_id,
            "workouts": []
        }

    try:
        raw_workouts = get_user_workouts(
            user_id.strip()
        )

        formatted_workouts = []

        for workout in raw_workouts:

            completed_at = workout.get(
                "completed_at"
            )

            if completed_at is not None:

                if hasattr(
                    completed_at,
                    "isoformat"
                ):
                    completed_at_str = (
                        completed_at.isoformat()
                    )
                else:
                    completed_at_str = str(
                        completed_at
                    )

            else:
                completed_at_str = None

            formatted_workouts.append({
                "user_id": str(
                    workout.get(
                        "user_id",
                        user_id
                    )
                ),
                "workout_name": str(
                    workout.get(
                        "workout_name",
                        "Workout"
                    )
                ),
                "duration_minutes": int(
                    workout.get(
                        "duration_minutes",
                        0
                    )
                ),
                "difficulty": int(
                    workout.get(
                        "difficulty",
                        1
                    )
                ),
                "completed_at": completed_at_str
            })

        # Sort newest completed workout first
        formatted_workouts.sort(
            key=lambda item:
                item.get("completed_at") or "",
            reverse=True
        )

        return {
            "user_id": user_id,
            "workouts": formatted_workouts
        }

    except Exception:
        return {
            "user_id": user_id,
            "workouts": []
        }