from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio
import google.genai as genai
import logging
from utils.config import config

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, prompt: str, system_prompt: str):
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        
        project_id = config.get("PROJECT_ID")
        location = config.get("LOCATION", "us-central1")
        
        if project_id:
            logger.info(f"Initializing Gemini via Vertex AI (Project: {project_id})")
            # Vertex AI initialization
            self.client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location
            )
        else:
            logger.info("Initializing Gemini via Google AI Studio")
            self.client = genai.Client(api_key=api_key)

    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        try:
            # For Gemini 2.0, we can use the unified generate_content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    'system_instruction': system_prompt,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini Provider Error: {e}")
            return f"Error: {str(e)}"

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config={
                    'system_instruction': system_prompt,
                }
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini Stream Error: {e}")
            yield f"Error: {str(e)}"

class VertexAIProvider(LLMProvider):
    """
    Specifically for Vertex AI using the standard vertexai SDK 
    (backup in case google-genai unified client has issues)
    """
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        from vertexai.generative_models import GenerativeModel
        self.model = GenerativeModel(model_name)

    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={"temperature": 0.2},
                system_instruction=system_prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"VertexAI Provider Error: {e}")
            return f"Error: {str(e)}"

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        try:
            responses = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.2},
                system_instruction=system_prompt,
                stream=True
            )
            for response in responses:
                yield response.text
        except Exception as e:
            logger.error(f"VertexAI Stream Error: {e}")
            yield f"Error: {str(e)}"

def get_llm_provider() -> LLMProvider:
    api_key = config.get("GOOGLE_API_KEY")
    model_name = config.get("LLM_MODEL", "gemini-2.0-flash")
    
    # We use GeminiProvider which now handles both Vertex and AI Studio
    return GeminiProvider(api_key=api_key, model_name=model_name)
