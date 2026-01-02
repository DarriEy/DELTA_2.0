from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: str

class ChatRequest(BaseModel):
    user_input: str
    conversation_id: int

class ConversationCreate(BaseModel):
    active_mode: str

class Conversation(BaseModel):
    id: int
    user_id: int
    start_time: datetime
    active_mode: str

class JobCreate(BaseModel):
    type: str = "SIMULATION"
    parameters: dict = {}

class Job(BaseModel):
    id: int
    status: str
    type: str
    parameters: dict
    created_at: datetime
    updated_at: datetime