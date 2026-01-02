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