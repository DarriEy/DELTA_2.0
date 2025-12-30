# backend/api/llm_integration.py
import base64
import os
import asyncio
import logging
import traceback
from io import BytesIO
from functools import partial
from typing import List, Optional, Dict, Any

import PIL.Image
import httpx
import google.auth
import google.auth.transport.requests
import google.genai as genai
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold
# from anthropic import Anthropic, AnthropicError  # Using Gemini instead
from dotenv import load_dotenv

from utils.config import config
from utils.prompts import (
    DELTA_SYSTEM_PROMPT,
    EDUCATIONAL_GUIDE_PROMPT,
)
from utils.google_utils import get_credentials
from modules.educational import get_educational_content

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PROJECT_ID = config.get("PROJECT_ID")
LOCATION = config.get("LOCATION", "us-central1")

# Initialize Clients - Use Gemini instead of Anthropic
# anthropic_client = Anthropic(api_key=config.get("ANTHROPIC_API_KEY"))

def init_vertex():
    """Initializes Vertex AI with the provided credentials."""
    try:
        creds = get_credentials()
        if creds:
            vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
            logger.info(f"Vertex AI initialized with project {PROJECT_ID}")
            return True
        else:
            logger.warning("No Google credentials found for Vertex AI.")
            return False
    except Exception as e:
        logger.error(f"Vertex AI init failed: {e}")
        return False

# Trigger initialization
vertex_ready = init_vertex()

async def generate_image(prompt: str) -> Optional[str]:
    """Generates an image using Imagen 3 via Vertex AI."""
    if not PROJECT_ID or not LOCATION:
        logger.error("PROJECT_ID or LOCATION not configured for image generation.")
        return None

    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagegeneration:predict"

    try:
        creds = get_credentials()
        if not creds:
            return None

        # Ensure credentials have a token
        auth_request = google.auth.transport.requests.Request()
        creds.refresh(auth_request)

        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        data = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": "16:9",
                "sampleCount": 1,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"Vertex AI Image Error: {response.status_code} - {response.text}")
                return None

            response_data = response.json()
            predictions = response_data.get("predictions")
            
            if predictions and len(predictions) > 0:
                base64_image = predictions[0].get("bytesBase64Encoded")
                if base64_image:
                    return f"data:image/png;base64,{base64_image}"
            
            return None

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

async def generate_gemini_response(prompt: str, system_prompt: str) -> str:
    """Generates a response using free Gemini API."""
    try:
        # Use free Gemini API
        api_key = config.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not configured. Please set GOOGLE_API_KEY."
        
        # Create client with API key
        client = genai.Client(api_key=api_key)
        
        # Combine system prompt with user prompt
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        return response.text
        
    except Exception as e:
        logger.error(f"Free Gemini API Error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

async def generate_response(user_input: str, role: str = "DELTA") -> str:
    """Main entry point for generating responses."""
    system_prompt = DELTA_SYSTEM_PROMPT if role == "DELTA" else EDUCATIONAL_GUIDE_PROMPT
    
    # Always use Gemini (free Google API)
    return await generate_gemini_response(user_input, system_prompt)

async def generate_summary_from_messages(messages: List[Dict[str, str]]) -> str:
    """Generates a summary of a conversation."""
    formatted_messages = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in messages])
    prompt = f"Please provide a concise scientific summary of the following conversation, highlighting key hydrological insights and action items:\n\n{formatted_messages}\n\nSummary:"
    
    # Always use Gemini
    return await generate_gemini_response(prompt, "You are a professional hydrological research summarizer.")