#!/usr/bin/env python3
"""Test workout logging endpoint."""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_log_workout():
    print("\n=== Testing POST /workout/log ===\n")

    payload = {
        "user_id": "demo_user_001",
        "workout_name": "Full Body Circuit",
        "duration_minutes": 45,
        "difficulty": 4
    }

    res = requests.post(f"{BASE_URL}/workout/log", json=payload)
    print(f"Status Code: {res.status_code}")

    if res.status_code == 200:
        data = res.json()
        print("[SUCCESS] Workout Logged Successfully:")
        print(f"  Status: {data.get('status')}")
        print(f"  Message:\n{data.get('message')}")
    else:
        print(f"Error Response: {res.text}")

if __name__ == "__main__":
    test_log_workout()
