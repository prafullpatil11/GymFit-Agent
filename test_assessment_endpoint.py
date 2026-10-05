#!/usr/bin/env python3
"""Test assessment endpoint."""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_assessment_endpoint():
    print("\n=== Testing POST /assessment ===\n")

    # 1. Create demo_user_001 first
    user_data = {
        "user_id": "demo_user_001",
        "name": "Demo User",
        "age": 21,
        "weight": 75.0,
        "height": 1.75,
        "fitness_level": "Beginner",
        "goal": "Fitness"
    }

    print("Step 1: Saving user profile via POST /users...")
    res_user = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {res_user.status_code}, Response: {res_user.text}")

    # 2. Call /assessment
    print("\nStep 2: Requesting assessment via POST /assessment...")
    payload = {"user_id": "demo_user_001"}
    res_assess = requests.post(f"{BASE_URL}/assessment", json=payload)
    print(f"Status Code: {res_assess.status_code}")
    
    if res_assess.status_code == 200:
        data = res_assess.json()
        print("[SUCCESS] Assessment retrieved successfully:")
        print(f"  Status: {data.get('status')}")
        print(f"  User ID: {data.get('user_id')}")
        print(f"  Profile: {data.get('profile')}")
        print(f"  Result Output:\n{data.get('assessment_result')}")
    else:
        print(f"Error Response: {res_assess.text}")

if __name__ == "__main__":
    test_assessment_endpoint()
