# backend/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration settings
config = {
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
    "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    "PROJECT_ID": os.environ.get("PROJECT_ID"),
    "LOCATION": os.environ.get("LOCATION", "us-central1"),
    "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
    
    # Model configuration
    "LLM_MODEL": os.environ.get("LLM_MODEL", "gemini-2.0-flash"), # Use 2.0 Flash for speed and scientific rigor
    "IMAGE_MODEL": "imagen-3",
    
    # Scientific settings
    "HYDRO_MODEL_BASE_URL": os.environ.get("HYDRO_MODEL_BASE_URL", "http://localhost:8080"),
}