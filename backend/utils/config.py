# backend/utils/config.py
import os
# Configuration settings
config = {
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
    #"LLM_MODEL": "gemini-1.0-pro",  # Add this line
    "LLM_MODEL": "claude-3-sonnet-20240229",
    "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    "PROJECT_ID": os.environ.get("PROJECT_ID"),
    "LOCATION": os.environ.get("LOCATION"),
    "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
}