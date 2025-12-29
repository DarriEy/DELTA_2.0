# backend/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    registration_date: datetime

    class Config:
        from_attributes = True

class UserInput(BaseModel):
    user_input: str

class ConversationBase(BaseModel):
    active_mode: str

class ImagePrompt(BaseModel):
    prompt: str 

class ConversationCreate(ConversationBase):
    user_id: Optional[int] = None

class Conversation(ConversationBase):
    id: Optional[int] = None
    conversation_id: Optional[int] = None
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    sender: str

class MessageCreate(MessageBase):
    message_index: int

class Message(MessageBase):
    message_id: int
    conversation_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ModelConfigBase(BaseModel):
    config_name: str
    model_name: str
    config_data: dict
    model_config = {'protected_namespaces': ()}

class ConversationUpdate(BaseModel):
    summary: Optional[str] = None
    end_time: Optional[datetime] = None
    active_mode: Optional[str] = None

class ModelConfigCreate(ModelConfigBase):
    pass

class ModelConfig(ModelConfigBase):
    config_id: int
    user_id: int
    creation_time: datetime

    class Config:
        from_attributes = True

class ModelRunBase(BaseModel):
    status: str
    output_path: Optional[str]

class ModelRunCreate(ModelRunBase):
    config_id : int

class ModelRun(ModelRunBase):
    run_id: int
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

# Consider moving this to a separate module or routes.py if it's only used there
class RunConfluenceInput(BaseModel):
    model: str
    configPath: str