from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.db import get_db
from ..models import Conversation as DBConversation, Message as DBMessage
from ..services.user_service import get_user_service
from ..schemas import (
    UserCreate, User, 
    ConversationCreate, Conversation, ConversationUpdate,
    MessageCreate, Message, APIResponse
)
from typing import List

router = APIRouter()

@router.post("/users/", response_model=APIResponse[User])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_service().get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        new_user = get_user_service().create_user(db, user.username, user.email, user.password)
        return APIResponse(data=new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/conversations/", response_model=APIResponse[Conversation])
def create_conversation(
    conversation: ConversationCreate, db: Session = Depends(get_db)
):
    try:
        db_conversation = get_user_service().create_conversation(db, conversation.dict())
        return APIResponse(data=db_conversation)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/conversations/{user_id}", response_model=APIResponse[List[Conversation]])
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(DBConversation).filter(DBConversation.user_id == user_id).all()
    return APIResponse(data=conversations)

@router.get("/messages/{conversation_id}", response_model=APIResponse[List[Message]])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index)
        .all()
    )
    return APIResponse(data=messages)

@router.post("/messages/", response_model=APIResponse[Message])
def create_message(
    message: MessageCreate, db: Session = Depends(get_db)
):
    db_message = DBMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return APIResponse(data=db_message)

@router.put("/conversations/{conversation_id}", response_model=APIResponse[Conversation])
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
        return APIResponse(data=conversation)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
