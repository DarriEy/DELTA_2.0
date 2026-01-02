from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import create_access_token, get_current_user
from ..schemas import (
    User, 
    ConversationCreate, Conversation,
    APIResponse
)
from typing import List, Optional
import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/users/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    if form_data.username == "commander" and form_data.password == "delta123":
        access_token = create_access_token(data={"sub": "commander"})
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {"id": 101, "username": "commander", "email": "commander@delta.ai"}
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

@router.get("/users/me", response_model=APIResponse[User])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return APIResponse(data=current_user)

@router.post("/conversations/", response_model=APIResponse[Conversation])
def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    # Return a stateless mock conversation
    mock_conv = {
        "id": 999, 
        "user_id": current_user["id"] if isinstance(current_user, dict) else current_user.id, 
        "start_time": datetime.datetime.now(), 
        "active_mode": conversation.active_mode
    }
    return APIResponse(data=mock_conv)

@router.get("/conversations/", response_model=APIResponse[List[Conversation]])
def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    return APIResponse(data=[])

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
        if db:
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
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
