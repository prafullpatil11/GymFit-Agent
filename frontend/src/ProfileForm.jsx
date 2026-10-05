import { useState } from "react";

/**
 * ProfileForm – UI for creating or updating a user profile.
 * It posts the profile to the FastAPI `/users` endpoint and then
 * retrieves the stored document via GET `/users/{user_id}`.
 */
export default function ProfileForm() {
  const [form, setForm] = useState({
    user_id: "",
    name: "",
    age: "",
    weight: "",
    height: "",
    fitness_level: "",
    goal: ""
  });

  const [savedProfile, setSavedProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const saveProfile = async () => {
    const userId = form.user_id.trim();

    if (!userId) {
      alert("User ID is required");
      return;
    }

    if (!form.name.trim()) {
      alert("Name is required");
      return;
    }

    if (!form.age || Number(form.age) <= 0) {
      alert("Please enter a valid age");
      return;
    }

    if (!form.weight || Number(form.weight) <= 0) {
      alert("Please enter a valid weight");
      return;
    }

    if (!form.height || Number(form.height) <= 0) {
      alert("Please enter a valid height");
      return;
    }

    if (!form.fitness_level.trim()) {
      alert("Fitness level is required");
      return;
    }

    if (!form.goal.trim()) {
      alert("Goal is required");
      return;
    }

    setLoading(true);
    setSavedProfile(null);

    try {
      // =====================================================
      // SAVE / UPDATE PROFILE
      // =====================================================

      const postRes = await fetch(
        "http://127.0.0.1:8000/users",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            user_id: userId,
            name: form.name.trim(),
            age: Number(form.age),
            weight: Number(form.weight),
            height: Number(form.height),
            fitness_level: form.fitness_level.trim(),
            goal: form.goal.trim()
          })
        }
      );

      const postData = await postRes.json();

      if (!postRes.ok) {
        throw new Error(
          postData.detail ||
          postData.error ||
          "Failed to save profile."
        );
      }

      // =====================================================
      // RETRIEVE SAVED PROFILE
      // =====================================================

      const getRes = await fetch(
        `http://127.0.0.1:8000/users/${encodeURIComponent(userId)}`
      );

      const getData = await getRes.json();

      if (!getRes.ok) {
        throw new Error(
          getData.detail ||
          getData.error ||
          "Profile was saved but could not be retrieved."
        );
      }

      // Handle the old backend tuple-style response too.
      if (
        Array.isArray(getData) &&
        getData.length === 2 &&
        getData[0]?.error
      ) {
        throw new Error(getData[0].error);
      }

      setSavedProfile(getData);

    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>User Profile</h2>

      <label>User ID</label>
      <input
        type="text"
        name="user_id"
        placeholder="Enter unique user ID"
        value={form.user_id}
        onChange={handleChange}
      />

      <label>Name</label>
      <input
        type="text"
        name="name"
        placeholder="Name"
        value={form.name}
        onChange={handleChange}
      />

      <label>Age</label>
      <input
        type="number"
        name="age"
        placeholder="Age"
        value={form.age}
        onChange={handleChange}
      />

      <label>Weight (kg)</label>
      <input
        type="number"
        name="weight"
        placeholder="Weight"
        value={form.weight}
        onChange={handleChange}
      />

      <label>Height (m)</label>
      <input
        type="number"
        step="0.001"
        name="height"
        placeholder="Height"
        value={form.height}
        onChange={handleChange}
      />

      <label>Fitness Level</label>
      <input
        type="text"
        name="fitness_level"
        placeholder="e.g., Beginner"
        value={form.fitness_level}
        onChange={handleChange}
      />

      <label>Goal</label>
      <input
        type="text"
        name="goal"
        placeholder="e.g., Weight Loss"
        value={form.goal}
        onChange={handleChange}
      />

      <button
        onClick={saveProfile}
        disabled={loading}
        style={{ marginTop: "1rem" }}
      >
        {loading ? "Saving…" : "Save Profile"}
      </button>

      {savedProfile && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3
            style={{
              color: "#dce1ec",
              fontSize: "18px",
              marginBottom: "0.5rem"
            }}
          >
            Saved Profile
          </h3>

          <pre
            style={{
              background: "#101219",
              color: "#e5e7eb",
              border: "1px solid #2d3240",
              borderRadius: "8px",
              padding: "1rem",
              whiteSpace: "pre-wrap",
              fontFamily: "monospace",
              fontSize: "14px"
            }}
          >
            {JSON.stringify(savedProfile, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}