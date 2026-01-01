from sqlalchemy.orm import Session
import bcrypt
from ..models import User as DBUser, Conversation as DBConversation

def create_user(db: Session, username: str, email: str, password: str):
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

def get_user_by_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()

def create_conversation(db: Session, conversation_data: dict):
    db_conversation = DBConversation(**conversation_data)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation
