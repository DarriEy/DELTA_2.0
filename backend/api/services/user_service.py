from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import bcrypt
from ..models import User as DBUser, Conversation as DBConversation

class UserService:
    def create_user(self, db: Session, username: str, email: str, password: str) -> DBUser:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        db_user = DBUser(
            username=username, email=email, password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_email(self, db: Session, email: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.email == email).first()

    def create_conversation(self, db: Session, conversation_data: Dict[str, Any]) -> DBConversation:
        db_conversation = DBConversation(**conversation_data)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation

_SERVICE: Optional[UserService] = None

def get_user_service() -> UserService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = UserService()
    return _SERVICE