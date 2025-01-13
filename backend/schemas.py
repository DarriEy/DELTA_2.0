# backend/schemas.py
from pydantic import BaseModel, EmailStr
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
        orm_mode = True

class ConversationBase(BaseModel):
    active_mode: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    conversation_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        orm_mode = True

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
        orm_mode = True

class ModelConfigBase(BaseModel):
    config_name: str
    model_name: str
    config_data: dict

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
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True
