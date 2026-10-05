#!/usr/bin/env python3
"""Test new user endpoints."""

import sys
sys.path.insert(0, "D:/FitAgent/venv/Lib/site-packages")

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_user():
    print("\n=== Testing POST /users (create/update user) ===\n")

    user_data = {
        "user_id": "test_user_001",
        "name": "Test User",
        "age": 21,
        "weight": 75.0,
        "height": 1.75,
        "fitness_level": "Beginner",
        "goal": "General Fitness"
    }

    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        print("[SUCCESS] User created successfully")

    # Update same user
    print("\n--- Testing update of same user ---")
    user_data["goal"] = "Weight Loss"

    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def test_get_user():
    print("\n=== Testing GET /users/{user_id} ===\n")

    response = requests.get(f"{BASE_URL}/users/test_user_001")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print(f"[SUCCESS] User retrieved: {user.get('name')}")
        print(f"  Goal: {user.get('goal')}")
        print(f"  User ID: {user.get('user_id')}")
    else:
        print(f"Response: {response.text}")

    # Non-existent user
    print("\n--- Testing non-existent user ---")
    response = requests.get(f"{BASE_URL}/users/nonexistent_user")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_create_user()
    test_get_user()