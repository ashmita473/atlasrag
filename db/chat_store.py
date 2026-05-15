from sqlalchemy.orm import Session

from db.models import ChatSession
from db.models import Message


class ChatStore:

    def create_session(
        self,
        db: Session,
        user_id: str
    ) -> ChatSession:

        session = ChatSession(
            user_id=user_id
        )

        db.add(session)

        db.commit()

        db.refresh(session)

        return session

    def save_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str
    ) -> Message:

        msg = Message(
            session_id=session_id,
            role=role,
            content=content
        )

        db.add(msg)

        db.commit()

        db.refresh(msg)

        return msg

    def get_messages(
        self,
        db: Session,
        session_id: str
    ) -> list:

        messages = db.query(Message).filter_by(
            session_id=session_id
        ).all()

        return messages