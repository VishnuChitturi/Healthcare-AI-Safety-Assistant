from modules.decision_engine import process_query
from modules.response_generator import generate_response
from modules.retrieval_layer import ingest_guidelines

# Seed database on startup
ingest_guidelines()

print("Healthcare AI Assistant Started")
print("Type 'exit' to stop.")
print("Type 'reset' to clear conversation.\n")

conversation_context = []

while True:

    query = input("Enter your medical query: ").strip()

    if query.lower() == "exit":
        print("System stopped.")
        break

    elif query.lower() == "reset":
        conversation_context = []
        print("Conversation reset.\n")
        continue

    # Add input to context
    conversation_context.append(query)

    # DEBUG (very useful)
    print("\nCurrent Context:", " | ".join(conversation_context[-3:]))

    # Process query
    decision = process_query(conversation_context)

    response = generate_response(query, decision)

    print("\nDecision:", decision)

    print("\nResponse:")
    print(response)

    print("\n" + "-" * 60)