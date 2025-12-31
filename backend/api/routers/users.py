from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models import get_db, Conversation as DBConversation, Message as DBMessage
from ..services import user_service
from ..schemas import (
    UserCreate, User, 
    ConversationCreate, Conversation, ConversationUpdate,
    MessageCreate, Message
)
from typing import List

router = APIRouter()

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        return user_service.create_user(db, user.username, user.email, user.password)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/conversations/", response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate, db: Session = Depends(get_db)
):
    try:
        db_conversation = user_service.create_conversation(db, conversation.dict())
        return db_conversation
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/conversations/{user_id}", response_model=List[Conversation])
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    return db.query(DBConversation).filter(DBConversation.user_id == user_id).all()

@router.get("/messages/{conversation_id}", response_model=List[Message])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    return (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index)
        .all()
    )

@router.post("/messages/", response_model=Message)
def create_message(
    message: MessageCreate, conversation_id: int, db: Session = Depends(get_db)
):
    db_message = DBMessage(**message.dict(), conversation_id=conversation_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.put("/conversations/{conversation_id}", response_model=Conversation)
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
):
    try:
        conversation = db.query(DBConversation).get(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        update_data = conversation_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)

        db.commit()
        db.refresh(conversation)
        return conversation
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
