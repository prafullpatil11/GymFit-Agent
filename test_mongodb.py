from database.connection import client, db


print("Testing MongoDB connection...")


try:
    # Send a ping command to MongoDB Atlas
    result = client.admin.command("ping")

    print("MongoDB connection successful!")
    print("Ping result:", result)

    print("Database:", db.name)

except Exception as e:
    print("MongoDB connection failed.")
    print("Error:", e)