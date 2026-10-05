from database.models import create_user_document
from database.crud import save_user, get_user, users_collection


print("Testing MongoDB CRUD...")


# Create test user
user = create_user_document(
    user_id="test_user_001",
    name="Test User",
    age=21,
    weight=75,
    height=1.75,
    fitness_level="Beginner",
    goal="General Fitness"
)


# Save user
user_id = save_user(user)

print("User saved successfully!")
print("MongoDB ID:", user_id)


# Retrieve user
saved_user = get_user("test_user_001")

print("Retrieved user:")
print(saved_user)


# Delete test user
users_collection.delete_one(
    {"user_id": "test_user_001"}
)

print("Test user deleted.")
print("CRUD test completed successfully!")