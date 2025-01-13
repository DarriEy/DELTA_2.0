# backend/schemas.py
from pydantic import BaseModel, Field, EmailStr  # Remove the type: ignore comment
from typing import List, Optional
from datetime import datetime

# Define UserBase first
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

# Conversation Models
class ConversationBase(BaseModel):
    active_mode: str
    

class ConversationCreate(ConversationBase):
    active_mode: str
    user_id: int

class Conversation(ConversationBase):
    conversation_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    summary: Optional[str] = None # Add this line
    

    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    summary: Optional[str] = None
    end_time: Optional[datetime] = None
    active_mode: Optional[str] = None

# Message Models (You were missing these)
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

# Model Configuration Models (Assuming you need these)
class ModelConfigBase(BaseModel):
    config_name: str
    model_type: str  # Renamed from model_name
    config_data: dict

class ModelConfigCreate(ModelConfigBase):
    pass

class ModelConfig(ModelConfigBase):
    config_id: int
    user_id: int
    creation_time: datetime

    class Config:
        from_attributes = True

# Model Run Models (Assuming you need these)
class ModelRunBase(BaseModel):
    status: str
    output_path: Optional[str]

class ModelRunCreate(ModelRunBase):
    config_id: int

class ModelRun(ModelRunBase):
    run_id: int
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True

# Educational Progress Models (Assuming you need these)
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

# Other Models
class UserInput(BaseModel):
    user_input: str

class ImagePrompt(BaseModel):
    prompt: str = Field(
        description="The text prompt for image generation", min_length=5, max_length=1000
    )

# Consider moving this to a separate module or routes.py if it's only used there
class RunConfluenceInput(BaseModel):
    model: str
    configPath: str