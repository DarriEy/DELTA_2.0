from abc import ABC, abstractmethod
from typing import List, Dict, Optional
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
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini Provider Error: {e}")
            return f"Error: {str(e)}"

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=full_prompt
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini Stream Error: {e}")
            yield f"Error: {str(e)}"

class VertexAIProvider(LLMProvider):
    # Placeholder for Vertex AI implementation
    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        # Implementation logic for Vertex AI
        return "Vertex AI response placeholder"

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        yield "Vertex AI streaming placeholder"

def get_llm_provider() -> LLMProvider:
    api_key = config.get("GOOGLE_API_KEY")
    model_name = config.get("LLM_MODEL", "gemini-2.0-flash")
    # For now, default to GeminiProvider
    return GeminiProvider(api_key=api_key, model_name=model_name)
