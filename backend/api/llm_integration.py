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
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold
from anthropic import Anthropic, AnthropicError
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

# Initialize Clients
anthropic_client = Anthropic(api_key=config.get("ANTHROPIC_API_KEY"))

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
    """Generates a response using Gemini 1.5 via Vertex AI."""
    if not vertex_ready:
        return "Vertex AI is not initialized. Please check credentials."
        
    try:
        # Check environment first for more dynamic behavior
        model_name = os.environ.get("LLM_MODEL") or config.get("LLM_MODEL", "gemini-1.5-flash")
        
        # Clean up model name
        if "claude" in model_name.lower():
            model_name = "gemini-1.5-flash"
        
        # Ensure it has the right prefix/suffix if needed, 
        # but Vertex usually just takes 'gemini-1.5-flash'
        
        model = GenerativeModel(
            model_name=model_name,
            system_instruction=[system_prompt]
        )
        
        safety_settings = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH),
        ]

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(model.generate_content, prompt, safety_settings=safety_settings)
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini (Vertex) Error: {e}")
        return f"Sorry, I encountered an error with the Google backend: {str(e)}"

async def generate_anthropic_response(prompt: str, system_prompt: str) -> str:
    """Generates a response using Anthropic Claude."""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                anthropic_client.messages.create,
                model=config.get("LLM_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
        )
        return response.content[0].text
    except AnthropicError as e:
        logger.error(f"Anthropic Error: {e}")
        return f"Claude Error: {str(e)}"

async def generate_response(user_input: str, role: str = "DELTA") -> str:
    """Main entry point for generating responses."""
    system_prompt = DELTA_SYSTEM_PROMPT if role == "DELTA" else EDUCATIONAL_GUIDE_PROMPT
    preferred_model = config.get("LLM_MODEL", "").lower()
    
    if "gemini" in preferred_model or not config.get("ANTHROPIC_API_KEY"):
        return await generate_gemini_response(user_input, system_prompt)
    else:
        if role == "EDUCATIONAL_GUIDE":
            return await generate_anthropic_with_tools(user_input, system_prompt)
        return await generate_anthropic_response(user_input, system_prompt)

async def generate_anthropic_with_tools(user_input: str, system_prompt: str) -> str:
    """Handles Anthropic tool use for educational content."""
    functions = [
        {
            "name": "get_educational_content",
            "description": "Provides educational content on a given hydrological topic.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The hydrological topic to explain (e.g., 'hydrological cycle', 'watershed').",
                    },
                },
                "required": ["topic"],
            },
        }
    ]

    try:
        response = anthropic_client.messages.create(
            model=config.get("LLM_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}],
            tools=functions,
        )

        if response.content and response.content[0].type == "tool_use":
            tool_call = response.content[0]
            if tool_call.name == "get_educational_content":
                topic = tool_call.input.get("topic")
                content = get_educational_content(topic)

                messages = [
                    {"role": "user", "content": user_input},
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": tool_call.id,
                                "name": tool_call.name,
                                "input": tool_call.input,
                            },
                            {"type": "text", "text": f"Retrieved content for {topic}: {content}"}
                        ]
                    }
                ]

                final_response = anthropic_client.messages.create(
                    model=config.get("LLM_MODEL", "claude-3-sonnet-20240229"),
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages,
                )
                return final_response.content[0].text

        return response.content[0].text
    except Exception as e:
        logger.error(f"Error in Anthropic tools: {e}")
        return f"Error: {str(e)}"

async def generate_summary_from_messages(messages: List[Dict[str, str]]) -> str:
    """Generates a summary of a conversation."""
    formatted_messages = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in messages])
    prompt = f"Please provide a concise scientific summary of the following conversation, highlighting key hydrological insights and action items:\n\n{formatted_messages}\n\nSummary:"
    
    preferred_model = config.get("LLM_MODEL", "").lower()
    if "gemini" in preferred_model or not config.get("ANTHROPIC_API_KEY"):
        return await generate_gemini_response(prompt, "You are a professional hydrological research summarizer.")
    else:
        return await generate_anthropic_response(prompt, "You are a professional hydrological research summarizer.")