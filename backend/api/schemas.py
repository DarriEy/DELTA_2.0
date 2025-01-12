# backend/api/schemas.py
from pydantic import BaseModel, Field

class ImagePrompt(BaseModel):
    prompt: str = Field(..., description="The text prompt for image generation", min_length=5, max_length=1000)


class UserInput(BaseModel):
    user_input: str

class ImagePrompt(BaseModel):
    prompt: str

class RunConfluenceInput(BaseModel):
    model: str
    configPath: str