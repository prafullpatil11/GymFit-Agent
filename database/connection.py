import os

from pymongo import MongoClient
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Get MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI")


if not MONGODB_URI:
    raise ValueError(
        "MONGODB_URI is not set in the .env file."
    )


# Create MongoDB client
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)


# Select GymFit database
db = client["GymFitDB"]