from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from ..models import User as DBUser, Conversation as DBConversation, Message as DBMessage

class UserService:
    def create_user(self, db: Session, username: str, email: str, password: str) -> DBUser:
        from ..auth import get_password_hash
        hashed_password = get_password_hash(password)
        db_user = DBUser(
            username=username, email=email, password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_email(self, db: Session, email: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.email == email).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.username == username).first()

    def create_conversation(self, db: Session, conversation_data: Dict[str, Any]) -> DBConversation:
        db_conversation = DBConversation(**conversation_data)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation

    def get_conversations_by_user(self, db: Session, user_id: int) -> List[DBConversation]:
        return db.query(DBConversation).filter(DBConversation.user_id == user_id).all()

    def get_conversation(self, db: Session, conversation_id: int) -> Optional[DBConversation]:
        return db.query(DBConversation).filter(DBConversation.id == conversation_id).first()

    def update_conversation(self, db: Session, conversation_id: int, update_data: Dict[str, Any]) -> Optional[DBConversation]:
        conversation = self.get_conversation(db, conversation_id)
        if not conversation:
            return None
        
        for key, value in update_data.items():
            setattr(conversation, key, value)
            
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_messages_by_conversation(self, db: Session, conversation_id: int) -> List[DBMessage]:
        return (
            db.query(DBMessage)
            .filter(DBMessage.conversation_id == conversation_id)
            .order_by(DBMessage.message_index)
            .all()
        )

    def create_message(self, db: Session, message_data: Dict[str, Any]) -> DBMessage:
        db_message = DBMessage(**message_data)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

_SERVICE: Optional[UserService] = None

def get_user_service() -> UserService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = UserService()
    return _SERVICE