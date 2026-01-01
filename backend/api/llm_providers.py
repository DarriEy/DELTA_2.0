from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
import inspect
import os
import logging
import asyncio
import functools

try:
    import google.genai as genai
    from google.genai import types
except ImportError:  # pragma: no cover - optional dependency
    genai = None
    types = None

from utils.config import Settings

logger = logging.getLogger(__name__)
GENAI_AVAILABLE = genai is not None

def retry_with_backoff(max_attempts=5, base_delay=2, backoff_factor=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        if attempt >= max_attempts:
                            logger.error(f"Gemini API: Max retry attempts reached. Last error: {err_msg}")
                            raise e
                        
                        # Try to extract suggested retry time from error message
                        # e.g., "Please retry in 45.339867259s"
                        delay = base_delay * (backoff_factor ** (attempt - 1))
                        import re
                        match = re.search(r"retry in ([\d\.]+)s", err_msg)
                        if match:
                            suggested_delay = float(match.group(1)) + 1.0 # Add a buffer
                            delay = max(delay, suggested_delay)
                        
                        logger.warning(f"Gemini API rate limited (429). Retrying in {delay:.2f}s (Attempt {attempt}/{max_attempts})...")
                        await asyncio.sleep(delay)
                    else:
                        raise e
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, prompt: str, system_prompt: str):
        pass
    
    # Optional methods for history support
    async def generate_response_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]], tools: Optional[List[Any]] = None) -> Union[str, Dict[str, Any]]:
        return await self.generate_response(prompt, system_prompt)

    async def generate_response_stream_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]]):
        async for chunk in self.generate_response_stream(prompt, system_prompt):
            yield chunk

class GeminiProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash",
        project_id: Optional[str] = None,
        location: str = "us-central1",
    ):
        from utils.google_utils import get_credentials
        self.api_key = api_key
        self.model_name = model_name
        
        self.project_id = project_id
        self.location = location
        
        self.client = None

        if not genai:
            logger.error("google.genai is not installed. Gemini provider unavailable.")
            return
        
        if project_id:
            try:
                logger.info(f"Attempting to initialize Gemini via Vertex AI (Project: {project_id})")
                creds = get_credentials()
                
                # Check if we actually got credentials and if the file path (if any) exists
                creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if creds or (creds_path and os.path.exists(creds_path)):
                    self.client = genai.Client(
                        vertexai=True,
                        project=project_id,
                        location=location,
                        credentials=creds
                    )
                    logger.info("Vertex AI initialization successful")
                else:
                    logger.warning("No valid credentials for Vertex AI found, will fallback to AI Studio")
            except Exception as e:
                logger.error(f"Vertex AI initialization failed, falling back to AI Studio: {e}")
        
        if not self.client:
            logger.info("Initializing Gemini via Google AI Studio")
            self.client = genai.Client(api_key=api_key)

    def _format_history(self, history: List[Dict[str, Any]]) -> List[types.Content]:
        """Formats internal history format to Gemini content objects."""
        formatted_contents = []
        for msg in history:
            role = "user" if msg.get("role") == "user" or msg.get("sender") == "user" else "model"
            content = msg.get("content", "")
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=content)]
                )
            )
        return formatted_contents

    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        return await self.generate_response_with_history(prompt, system_prompt, [])

    @retry_with_backoff(max_attempts=8, base_delay=2)
    async def generate_response_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]], tools: Optional[List[Any]] = None) -> Union[str, Dict[str, Any]]:
        if not self.client:
            return "Error: Gemini client not initialized. Check API keys and credentials."
        try:
            contents = []
            if history:
                contents.extend(self._format_history(history))
            
            # Add the current prompt
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

            config_params = {
                'system_instruction': system_prompt,
            }
            if tools:
                config_params['tools'] = tools

            # Use the async client (client.aio)
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config_params
            )
            
            if not response:
                logger.warning("Gemini returned an empty response")
                return "I'm sorry, I couldn't generate a response. Please try again."

            # Check for function calls
            function_calls = []
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_calls.append({
                            "name": part.function_call.name,
                            "args": part.function_call.args
                        })

            text_response = response.text or ""

            if function_calls:
                return {
                    "text": text_response,
                    "function_calls": function_calls
                }
            
            return text_response

        except Exception as e:
            # The decorator handles retrying for 429
            raise e

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        async for chunk in self.generate_response_stream_with_history(prompt, system_prompt, []):
            yield chunk

    @retry_with_backoff(max_attempts=8, base_delay=2)
    async def generate_response_stream_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]]):
        if not self.client:
            yield "Error: Gemini client not initialized."
            return
        try:
            contents = []
            if history:
                contents.extend(self._format_history(history))
            
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

            # Use the async client (client.aio) for streaming
            # Note: Streaming with tools is complex, omitting tools for stream for now or we can add them but need to handle non-text chunks
            stream = self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config={
                    'system_instruction': system_prompt,
                }
            )
            if inspect.isawaitable(stream):
                stream = await stream
            async for chunk in stream:
                if chunk and chunk.text:
                    yield chunk.text
        except Exception as e:
            # The decorator handles retrying for 429
            raise e

def get_llm_provider(settings: Settings) -> LLMProvider:
    api_key = settings.google_api_key
    model_name = settings.llm_model

    # We use GeminiProvider which now handles both Vertex and AI Studio
    return GeminiProvider(
        api_key=api_key,
        model_name=model_name,
        project_id=settings.project_id,
        location=settings.location,
    )
