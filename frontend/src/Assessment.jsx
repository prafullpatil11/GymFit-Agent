import { useState } from "react";

export default function Assessment() {
  const [userId, setUserId] = useState("");
  const [assessmentData, setAssessmentData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runAssessment = async () => {
    if (!userId.trim()) {
      alert("Please enter your User ID.");
      return;
    }

    setLoading(true);
    setAssessmentData(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/assessment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || "Failed to run fitness assessment.");
      }

      setAssessmentData(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Extract BMI value from assessment_result if present
  const getBmiDisplay = () => {
    if (!assessmentData || !assessmentData.assessment_result) return null;

    const text = assessmentData.assessment_result;
    // Look for BMI in text output, e.g., "BMI: 24.49" or "BMI calculated: 24.49"
    const match = text.match(/BMI:\s*([\d.]+)/i) || text.match(/([\d.]+)/);
    
    // If structured match found return match[1], else return text directly
    return match ? match[1] : text;
  };

  return (
    <section className="card">
      <h2>Fitness Assessment</h2>

      <label>User ID</label>
      <input
        type="text"
        placeholder="Enter your User ID (e.g. demo_user_001)"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
      />

      <button onClick={runAssessment} disabled={loading} style={{ marginTop: "1rem" }}>
        {loading ? "Running Assessment..." : "Run Fitness Assessment"}
      </button>

      {assessmentData && (
        <div className="card result" style={{ marginTop: "1.5rem" }}>
          <h3>Fitness Assessment</h3>
          <div className="assessment-details" style={{ lineHeight: "1.8", marginTop: "1rem" }}>
            <p><strong>Name:</strong> {assessmentData.profile?.name}</p>
            <p><strong>Age:</strong> {assessmentData.profile?.age}</p>
            <p><strong>Weight:</strong> {assessmentData.profile?.weight} kg</p>
            <p><strong>Height:</strong> {assessmentData.profile?.height} m</p>
            <p><strong>Fitness Level:</strong> {assessmentData.profile?.fitness_level}</p>
            <p><strong>Goal:</strong> {assessmentData.profile?.goal}</p>
            <p><strong>BMI:</strong> {getBmiDisplay()}</p>
          </div>
        </div>
      )}
    </section>
  );
}
