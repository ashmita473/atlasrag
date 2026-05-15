# db/models.py


from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import uuid
 
class Base(DeclarativeBase):
    pass

# Stores registered users
class User(Base):
    __tablename__ = 'users'
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username      = Column(String, unique=True, nullable=False)
    hashed_pw     = Column(String, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
 
class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
class Message(Base):
    __tablename__ = 'messages'
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    role       = Column(String, nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
class QuizResult(Base):
    __tablename__ = 'quiz_results'
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String, nullable=False)
    score      = Column(Float, nullable=False)
    difficulty = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
