from app.memory.vector_memory import search_vector_memory


USER_ID = "test_memory_001"

query = "What workout preferences does this user have?"

print("\n=== VECTOR MEMORY INTEGRATION TEST ===\n")

memories = search_vector_memory(
    user_id=USER_ID,
    query=query,
    limit=3
)

if not memories:
    print("No relevant memories found.")
else:
    print("Relevant memories:\n")

    for memory in memories:
        print(
            f"- {memory['text']}"
        )
        print(
            f"  Type: {memory['memory_type']}"
        )
        print(
            f"  Similarity Score: "
            f"{memory['score']:.4f}"
        )
        print()