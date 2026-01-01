from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from utils.db import get_db
from ..models import Conversation as DBConversation, Message as DBMessage, User as DBUser
from ..services.user_service import UserService, get_user_service
from ..auth import create_access_token, verify_password, get_current_user
from ..schemas import (
    UserCreate, User, 
    ConversationCreate, Conversation, ConversationUpdate,
    MessageCreate, Message, APIResponse
)
from typing import List

router = APIRouter()

@router.post("/users/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    user = user_service.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/users/me", response_model=APIResponse[User])
async def read_users_me(current_user: DBUser = Depends(get_current_user)):
    return APIResponse(data=current_user)

@router.post("/users/", response_model=APIResponse[User])
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    existing_user = user_service.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    existing_username = user_service.get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    try:
        new_user = user_service.create_user(db, user.username, user.email, user.password)
        return APIResponse(data=new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/conversations/", response_model=APIResponse[Conversation])
def create_conversation(
    conversation: ConversationCreate, 
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    current_user: DBUser = Depends(get_current_user)
):
    try:
        conv_dict = conversation.dict()
        conv_dict["user_id"] = current_user.id
        db_conversation = user_service.create_conversation(db, conv_dict)
        return APIResponse(data=db_conversation)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/conversations/", response_model=APIResponse[List[Conversation]])
def get_conversations(
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    current_user: DBUser = Depends(get_current_user)
):
    conversations = user_service.get_conversations_by_user(db, current_user.id)
    return APIResponse(data=conversations)

@router.get("/messages/{conversation_id}", response_model=APIResponse[List[Message]])
def get_messages(
    conversation_id: int, 
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify ownership
    conv = user_service.get_conversation(db, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    messages = user_service.get_messages_by_conversation(db, conversation_id)
    return APIResponse(data=messages)

@router.post("/messages/", response_model=APIResponse[Message])
def create_message(
    message: MessageCreate, 
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify ownership
    conv = user_service.get_conversation(db, message.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    try:
        db_message = user_service.create_message(db, message.dict())
        return APIResponse(data=db_message)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.put("/conversations/{conversation_id}", response_model=APIResponse[Conversation])
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    current_user: DBUser = Depends(get_current_user)
):
    # Verify ownership
    conv = user_service.get_conversation(db, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    try:
        update_data = conversation_update.dict(exclude_unset=True)
        conversation = user_service.update_conversation(db, conversation_id, update_data)
        return APIResponse(data=conversation)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
