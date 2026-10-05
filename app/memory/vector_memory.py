from datetime import datetime

from langchain_ollama import OllamaEmbeddings

from database.connection import db


# ==========================================================
# Embedding Model
# ==========================================================

embeddings = OllamaEmbeddings(
    model="embeddinggemma"
)


# ==========================================================
# MongoDB Collection
# ==========================================================

vector_memory_collection = db["vector_memory"]


# ==========================================================
# Store Vector Memory
# ==========================================================

def store_vector_memory(
    user_id: str,
    text: str,
    memory_type: str = "general"
):
    """
    Convert text into an embedding vector and store it
    in MongoDB as long-term vector memory.
    """

    if not user_id:
        raise ValueError("user_id is required.")

    if not text.strip():
        raise ValueError("Memory text cannot be empty.")

    vector = embeddings.embed_query(text)

    document = {
        "user_id": user_id,
        "text": text,
        "memory_type": memory_type,
        "embedding": vector,
        "created_at": datetime.now()
    }

    result = vector_memory_collection.insert_one(
        document
    )

    return str(result.inserted_id)


# ==========================================================
# Retrieve Stored Vector Memories
# ==========================================================

def get_user_vector_memories(
    user_id: str,
    limit: int = 10
):
    """
    Retrieve vector memories stored for a user.
    """

    if not user_id:
        return []

    memories = vector_memory_collection.find(
        {"user_id": user_id}
    ).sort(
        "created_at",
        -1
    ).limit(limit)

    return list(memories)


# ==========================================================
# Semantic Vector Search
# ==========================================================

def search_vector_memory(
    user_id: str,
    query: str,
    limit: int = 3
):
    """
    Search the user's long-term vector memories using
    semantic similarity.
    """

    if not user_id:
        return []

    if not query.strip():
        return []

    query_vector = embeddings.embed_query(query)

    results = vector_memory_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": max(limit * 10, 10),
                    "limit": limit
                }
            },
            {
                "$match": {
                    "user_id": user_id
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "user_id": 1,
                    "text": 1,
                    "memory_type": 1,
                    "created_at": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]
    )

    return list(results)