# backend/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInput(BaseModel):
    user_input: str

class ConversationBase(BaseModel):
    active_mode: str
    user_id: Optional[int] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    summary: Optional[str] = None
    active_mode: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    start_time: datetime
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    content: str
    sender: str
    conversation_id: int
    message_index: int

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ImagePrompt(BaseModel):
    prompt: str 

class ModelConfigBase(BaseModel):
    name: str
    parameters: dict

class ModelConfigCreate(ModelConfigBase):
    pass

class ModelConfig(ModelConfigBase):
    config_id: int
    model_config = ConfigDict(from_attributes=True)

class ModelRunBase(BaseModel):
    status: str
    output_path: Optional[str]

class ModelRunCreate(ModelRunBase):
    config_id : int

class ModelRun(ModelRunBase):
    run_id: int
    start_time: datetime

    model_config = ConfigDict(from_attributes=True)

class EducationalProgressBase(BaseModel):
    topic_name: str
    completion_status: bool
    quiz_score: Optional[int]

class EducationalProgressCreate(EducationalProgressBase):
    pass

class EducationalProgress(EducationalProgressBase):
    progress_id: int
    user_id: int
    last_accessed: datetime

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    type: str
    parameters: dict

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[dict] = None
    logs: Optional[str] = None

class Job(JobBase):
    id: int
    status: str
    result: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Consider moving this to a separate module or routes.py if it's only used there
class RunConfluenceInput(BaseModel):
    model: str
    configPath: str
