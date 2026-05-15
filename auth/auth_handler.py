# auth/auth_handler.py
import bcrypt
from sqlalchemy.orm import Session
from db.models import User
 
class AuthHandler:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
 
    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
 
    def register(self, db: Session, username: str, password: str) -> User:
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            raise ValueError(
                "Username already taken"
            )

        user = User(username=username, hashed_pw=self.hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
 
    def login(self, db: Session, username: str, password: str) -> User | None:
        user = db.query(User).filter_by(username=username).first()
        if user and self.verify_password(password, user.hashed_pw):
            return user
        return None
