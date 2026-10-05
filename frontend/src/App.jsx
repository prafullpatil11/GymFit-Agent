import { useState } from "react";
import "./App.css";
import ProfileForm from "./ProfileForm";
import Assessment from "./Assessment";

// Safe text formatter that renders bold text without raw markdown ** symbols
function FormattedText({ content }) {
  if (!content) return null;
  const text = typeof content === "object" ? (content.content || JSON.stringify(content, null, 2)) : String(content);

  const lines = text.split("\n");

  return (
    <div className="formatted-text-container" style={{ lineHeight: "1.6" }}>
      {lines.map((line, lineIdx) => {
        // Split line by **bold** markdown pattern
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        return (
          <div key={lineIdx} style={{ minHeight: "1.2em" }}>
            {parts.map((part, partIdx) => {
              if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
                return <strong key={partIdx}>{part.slice(2, -2)}</strong>;
              }
              return <span key={partIdx}>{part}</span>;
            })}
          </div>
        );
      })}
    </div>
  );
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = d.getDate();
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, "0");
    const mins = String(d.getMinutes()).padStart(2, "0");
    return `${day} ${month} ${year}, ${hours}:${mins}`;
  } catch {
    return dateStr;
  }
}

function App() {
  const [userId, setUserId] = useState("");
  const [days, setDays] = useState(3);
  const [equipment, setEquipment] = useState("No Equipment");
  const [message, setMessage] = useState("");

  const [workoutPlan, setWorkoutPlan] = useState("");
  const [approvalRequired, setApprovalRequired] = useState(false);

  const [feedback, setFeedback] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  const [finalResponse, setFinalResponse] = useState("");

  const [loading, setLoading] = useState(false);
  const [approvalLoading, setApprovalLoading] = useState(false);
  
  // -------------------------------------------------
  // Workout Logging State
  const [logWorkoutName, setLogWorkoutName] = useState("");
  const [logDuration, setLogDuration] = useState(30);
  const [logDifficulty, setLogDifficulty] = useState(3);
  const [logLoading, setLogLoading] = useState(false);
  const [logSuccessMessage, setLogSuccessMessage] = useState("");

  // -------------------------------------------------
  // Progress UI state
  const [progressLoading, setProgressLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");
  const [workoutHistory, setWorkoutHistory] = useState(null);

  // -------------------------------------------------
  // UI Tab management
  const [activeTab, setActiveTab] = useState("profile");

  // ==========================================================
  // Create Workout
  // ==========================================================

  const createWorkout = async () => {
    if (!userId.trim()) {
      alert("Please enter your User ID.");
      return;
    }

    setLoading(true);
    setWorkoutPlan("");
    setApprovalRequired(false);
    setFinalResponse("");
    setShowFeedback(false);
    setFeedback("");
    setLogSuccessMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/workout",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            user_message:
              message || "Create a workout plan for me",
            days: Number(days),
            equipment: equipment,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to create workout."
        );
      }

      setWorkoutPlan(data.workout_plan || "");

      setApprovalRequired(
        data.approval_required || false
      );
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };


  // ==========================================================
  // Approve Workout
  // ==========================================================

  const approveWorkout = async () => {
    setApprovalLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/workout/approval",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            status: "approve",
            feedback: "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to approve workout."
        );
      }

      setApprovalRequired(
        data.approval_required || false
      );

      setWorkoutPlan(
        data.workout_plan || workoutPlan
      );

      setFinalResponse(
        data.final_response || ""
      );

      setShowFeedback(false);

    } catch (error) {
      alert(error.message);
    } finally {
      setApprovalLoading(false);
    }
  };


  // ==========================================================
  // Show Rejection Feedback
  // ==========================================================

  const rejectWorkout = () => {
    setShowFeedback(true);
  };


  // ==========================================================
  // Submit Rejection
  // ==========================================================

  const submitRejection = async () => {
    if (!feedback.trim()) {
      alert("Please enter feedback for the revised workout.");
      return;
    }

    setApprovalLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/workout/approval",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            status: "reject",
            feedback: feedback,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to reject workout."
        );
      }

      setWorkoutPlan(
        data.workout_plan || ""
      );

      setApprovalRequired(
        data.approval_required || false
      );

      setShowFeedback(false);

      setFeedback("");

      setFinalResponse(
        data.final_response || ""
      );

    } catch (error) {
      alert(error.message);
    } finally {
      setApprovalLoading(false);
    }
  };


  const submitLogWorkout = async () => {
    if (!userId.trim()) {
      alert("Please enter your User ID.");
      return;
    }

    if (!logWorkoutName.trim()) {
      alert("Please enter the Workout Name.");
      return;
    }

    setLogLoading(true);
    setLogSuccessMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/workout/log",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            workout_name: logWorkoutName,
            duration_minutes: Number(logDuration),
            difficulty: Number(logDifficulty),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || data.error || "Failed to log workout."
        );
      }

      setLogSuccessMessage(data.message || "Workout logged successfully.");
      setLogWorkoutName("");
    } catch (error) {
      alert(error.message);
    } finally {
      setLogLoading(false);
    }
  };


  // ==========================================================
  // Progress Analysis & History
  // ==========================================================

  const submitAnalyzeProgress = async () => {
    if (!userId.trim()) {
      alert('Please enter your User ID.');
      return;
    }
    setProgressLoading(true);
    setProgressMessage('');
    setWorkoutHistory(null);

    try {
      // 1. Fetch progress analysis
      const progressPromise = fetch(
        'http://127.0.0.1:8000/progress/analyze',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user_id: userId }),
        }
      ).then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || data.message || 'Failed to analyze progress.');
        }
        return data.message || data.status;
      });

      // 2. Fetch workout history
      const historyPromise = fetch(
        `http://127.0.0.1:8000/users/${encodeURIComponent(userId.trim())}/workouts`
      ).then(async (res) => {
        if (!res.ok) {
          return [];
        }
        const data = await res.json();
        return Array.isArray(data.workouts) ? data.workouts : [];
      }).catch(() => []);

      const [progResult, histResult] = await Promise.all([progressPromise, historyPromise]);
      setProgressMessage(progResult);
      setWorkoutHistory(histResult);
    } catch (error) {
      alert(error.message);
    } finally {
      setProgressLoading(false);
    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="app">

      {/* =====================================================
          Header
      ===================================================== */}

      <header className="header">
        <h1>GymFit Agent</h1>

        <p>
          Agentic AI-Based Fitness & Workout
          Management System
        </p>
      </header>

      {/* Navigation Tabs */}
      <nav className="tabs" style={{ marginBottom: "1rem" }}>
        <button onClick={() => setActiveTab("profile")} disabled={activeTab === "profile"}>Profile</button>
        <button onClick={() => setActiveTab("assessment")} disabled={activeTab === "assessment"} style={{ marginLeft: "0.5rem" }}>Assessment</button>
        <button onClick={() => setActiveTab("workout")} disabled={activeTab === "workout"} style={{ marginLeft: "0.5rem" }}>Workout</button>
        <button onClick={() => setActiveTab("progress")} disabled={activeTab === "progress"} style={{ marginLeft: "0.5rem" }}>Progress</button>
      </nav>

      <main className="container">
        {activeTab === "profile" && <ProfileForm />}

        {activeTab === "assessment" && <Assessment />}

        {activeTab === "workout" && (
          <>
            {/* ===================================================
                Workout Form
            =================================================== */}

            <section className="card">

              <h2>Create Your Workout</h2>

              <label>User ID</label>

              <input
                type="text"
                placeholder="Enter your User ID"
                value={userId}
                onChange={(e) =>
                  setUserId(e.target.value)
                }
              />


              <label>What do you want?</label>

              <input
                type="text"
                placeholder="Create a workout plan for me"
                value={message}
                onChange={(e) =>
                  setMessage(e.target.value)
                }
              />


              <label>Workout Days</label>

              <select
                value={days}
                onChange={(e) =>
                  setDays(e.target.value)
                }
              >
                <option value={1}>1 Day</option>
                <option value={2}>2 Days</option>
                <option value={3}>3 Days</option>
                <option value={4}>4 Days</option>
                <option value={5}>5 Days</option>
                <option value={6}>6 Days</option>
                <option value={7}>7 Days</option>
              </select>


              <label>Equipment</label>

              <input
                type="text"
                value={equipment}
                onChange={(e) =>
                  setEquipment(e.target.value)
                }
              />


              <button
                onClick={createWorkout}
                disabled={loading}
              >
                {loading
                  ? "Creating Workout..."
                  : "Create Workout"}
              </button>

            </section>


            {/* ===================================================
                Workout Result
            =================================================== */}

            {workoutPlan && (

              <section className="card result">

                <h2>Proposed Workout</h2>

                <div style={{
                  background: "#101219",
                  border: "1px solid #2d3240",
                  borderRadius: "10px",
                  padding: "20px",
                  color: "#e5e7eb",
                  overflowX: "auto"
                }}>
                  <FormattedText content={workoutPlan} />
                </div>


                {/* =================================================
                    Human Approval
                ================================================= */}

                {approvalRequired && (

                  <div className="approval">

                    <h3>
                      Human Approval Required
                    </h3>

                    <p>
                      Please review the proposed workout
                      before continuing.
                    </p>


                    {/* =============================================
                        Approval Buttons
                    ============================================= */}

                    {!showFeedback && (

                      <div className="approval-buttons">

                        <button
                          onClick={approveWorkout}
                          disabled={approvalLoading}
                        >
                          {approvalLoading
                            ? "Processing..."
                            : "Approve"}
                        </button>


                        <button
                          className="reject"
                          onClick={rejectWorkout}
                          disabled={approvalLoading}
                        >
                          Reject
                        </button>

                      </div>

                    )}


                    {/* =============================================
                        Rejection Feedback
                    ============================================= */}

                    {showFeedback && (

                      <div className="feedback-section">

                        <label>
                          Why do you want to change
                          the workout?
                        </label>

                        <textarea
                          placeholder="Example: Make the workout easier."
                          value={feedback}
                          onChange={(e) =>
                            setFeedback(e.target.value)
                          }
                        />

                        <button
                          onClick={submitRejection}
                          disabled={approvalLoading}
                        >
                          {approvalLoading
                            ? "Creating Revised Workout..."
                            : "Submit Feedback"}
                        </button>

                      </div>

                    )}

                  </div>

                )}

              </section>

            )}


            {/* ===================================================
                Final Response
            =================================================== */}

            {finalResponse && (

              <section className="card result">

                <h2>Fitness Coach</h2>

                <div style={{
                  background: "#101219",
                  border: "1px solid #2d3240",
                  borderRadius: "10px",
                  padding: "20px",
                  color: "#e5e7eb",
                  overflowX: "auto"
                }}>
                  <FormattedText content={finalResponse} />
                </div>

              </section>

            )}


            {/* ===================================================
                Log Workout Section
            =================================================== */}

            <section className="card" style={{ marginTop: "1.5rem" }}>

              <h2>Log Completed Workout</h2>

              <label>User ID</label>

              <input
                type="text"
                placeholder="Enter your User ID"
                value={userId}
                onChange={(e) =>
                  setUserId(e.target.value)
                }
              />

              <label>Workout Name</label>

              <input
                type="text"
                placeholder="e.g. Upper Body Strength"
                value={logWorkoutName}
                onChange={(e) =>
                  setLogWorkoutName(e.target.value)
                }
              />

              <label>Duration (minutes)</label>

              <input
                type="number"
                placeholder="Duration in minutes"
                value={logDuration}
                onChange={(e) =>
                  setLogDuration(e.target.value)
                }
              />

              <label>Difficulty (1 - 5)</label>

              <select
                value={logDifficulty}
                onChange={(e) =>
                  setLogDifficulty(e.target.value)
                }
              >
                <option value={1}>1 - Very Easy</option>
                <option value={2}>2 - Easy</option>
                <option value={3}>3 - Moderate</option>
                <option value={4}>4 - Hard</option>
                <option value={5}>5 - Very Hard</option>
              </select>

              <button
                onClick={submitLogWorkout}
                disabled={logLoading}
                style={{ marginTop: "1rem" }}
              >
                {logLoading
                  ? "Logging Workout..."
                  : "Log Workout"}
              </button>

              {logSuccessMessage && (
                <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#e6fffa", color: "#234e52", borderRadius: "4px", border: "1px solid #b2f5ea" }}>
                  <strong>Success:</strong>
                  <pre style={{ margin: "0.5rem 0 0 0", whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
                    {logSuccessMessage}
                  </pre>
                </div>
              )}

            </section>
          </>
        )}
        {activeTab === "progress" && (
          <section className="card" style={{ marginTop: "1.5rem" }}>
            <h2>Progress Dashboard</h2>
            <label>User ID</label>
            <input
              type="text"
              placeholder="Enter your User ID"
              value={userId}
              onChange={e => setUserId(e.target.value)}
            />
            <button
              onClick={submitAnalyzeProgress}
              disabled={progressLoading}
              style={{ marginTop: "1rem" }}
            >
              {progressLoading ? "Analyzing..." : "Analyze Progress"}
            </button>

            {/* Progress Analysis Output */}
            {progressMessage && (
              <div style={{ marginTop: "1.5rem" }}>
                <h3 style={{ color: "#dce1ec", fontSize: "18px", marginBottom: "0.75rem" }}>
                  Progress Analysis
                </h3>
                <div style={{
                  background: "#101219",
                  color: "#e5e7eb",
                  border: "1px solid #2d3240",
                  borderRadius: "10px",
                  padding: "1.25rem"
                }}>
                  <FormattedText content={progressMessage} />
                </div>
              </div>
            )}

            {/* Workout History Output */}
            {workoutHistory !== null && (
              <div style={{ marginTop: "2rem" }}>
                <h3 style={{ color: "#dce1ec", fontSize: "18px", marginBottom: "0.75rem" }}>
                  Workout History
                </h3>

                {workoutHistory.length === 0 ? (
                  <p style={{ color: "#a8b0c0", fontStyle: "italic", margin: "0.5rem 0" }}>
                    No completed workouts found for this user.
                  </p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                    {workoutHistory.map((item, index) => (
                      <div
                        key={index}
                        style={{
                          background: "#101219",
                          border: "1px solid #2d3240",
                          borderRadius: "8px",
                          padding: "1rem 1.25rem"
                        }}
                      >
                        <h4 style={{ margin: "0 0 0.5rem 0", color: "#ffffff", fontSize: "16px" }}>
                          {item.workout_name}
                        </h4>
                        <div style={{ color: "#dce1ec", fontSize: "14px", lineHeight: "1.6" }}>
                          <div><strong>Duration:</strong> {item.duration_minutes} minutes</div>
                          <div><strong>Difficulty:</strong> {item.difficulty}/5</div>
                          {item.completed_at && (
                            <div style={{ color: "#a8b0c0", marginTop: "0.25rem" }}>
                              <strong>Completed:</strong> {formatDate(item.completed_at)}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>
        )}

      </main>

    </div>
  );
}

export default App;