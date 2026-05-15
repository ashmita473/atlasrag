import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from db.session import SessionLocal

from db.chat_store import ChatStore


db = SessionLocal()

store = ChatStore()


session = store.create_session(
    db,
    user_id="test-user"
)

print("\nSession Created:")
print(session.id)


store.save_message(
    db,
    session.id,
    "user",
    "Hello EduMind"
)

store.save_message(
    db,
    session.id,
    "assistant",
    "Hello Ashmita! How can I help?"
)


messages = store.get_messages(
    db,
    session.id
)

print("\n=== CHAT HISTORY ===\n")

for msg in messages:

    print(f"{msg.role.upper()}: {msg.content}")