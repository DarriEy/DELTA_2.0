from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
import inspect
import os
import logging
import asyncio
import functools
import json
import httpx

try:
    import google.genai as genai
    from google.genai import types
except ImportError:  # pragma: no cover - optional dependency
    genai = None
    types = None

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
except ImportError:
    ElevenLabs = None

from utils.config import Settings

logger = logging.getLogger(__name__)
GENAI_AVAILABLE = genai is not None

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
                creds = get_credentials()
                
                # Only attempt Vertex AI if we have real service account credentials
                # google.auth.default() can hang on non-GCP environments
                from google.oauth2 import service_account
                if isinstance(creds, service_account.Credentials):
                    logger.info(f"Attempting to initialize Gemini via Vertex AI (Project: {project_id})")
                    self.client = genai.Client(
                        vertexai=True,
                        project=project_id,
                        location=location,
                        credentials=creds
                    )
                    logger.info("Vertex AI initialization successful")
                else:
                    logger.warning("No Service Account credentials found, skipping Vertex AI to avoid hangs.")
            except Exception as e:
                logger.error(f"Vertex AI initialization skipped: {e}")
        
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

    async def generate_response_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]], tools: Optional[List[Any]] = None) -> Union[str, Dict[str, Any]]:
        if not self.client:
            return "Error: Gemini client not initialized. Check API keys and credentials."
        
        attempt = 0
        max_attempts = 5
        base_delay = 2
        
        while attempt < max_attempts:
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
                    return "I'm sorry, I couldn't generate a response."

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
                attempt += 1
                err_msg = str(e)
                
                if "404" in err_msg and self.model_name != "gemini-1.5-flash-latest":
                    logger.warning(f"Model {self.model_name} not found, falling back to 1.5-flash")
                    self.model_name = "gemini-1.5-flash-latest"
                    attempt = 0
                    continue

                if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_attempts:
                    import re
                    delay = base_delay * (2 ** (attempt - 1))
                    match = re.search(r"retry in ([\d\.]+)s", err_msg)
                    if match:
                        try:
                            delay = max(delay, float(match.group(1)) + 1.0)
                        except ValueError: pass
                    
                    logger.warning(f"Gemini API rate limited. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Gemini Error: {err_msg}")
                    return f"Error: {err_msg}"
        
        return "Error: Quota exceeded after retries."

    async def generate_response_stream(self, prompt: str, system_prompt: str):
        async for chunk in self.generate_response_stream_with_history(prompt, system_prompt, []):
            yield chunk

    async def generate_response_stream_with_history(self, prompt: str, system_prompt: str, history: List[Dict[str, Any]]):
        if not self.client:
            yield "Error: Gemini client not initialized."
            return

        attempt = 0
        max_attempts = 5
        base_delay = 2
        
        while attempt < max_attempts:
            try:
                contents = []
                if history:
                    contents.extend(self._format_history(history))
                
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

                stream_call = self.client.aio.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config={
                        'system_instruction': system_prompt,
                    }
                )
                
                # For some reason, sometimes we need to await the stream object itself
                if inspect.isawaitable(stream_call):
                    stream = await stream_call
                else:
                    stream = stream_call

                async for chunk in stream:
                    try:
                        if chunk and chunk.text:
                            yield chunk.text
                    except (AttributeError, ValueError) as e:
                        # This happens if chunk.text is not available (e.g. blocked)
                        logger.warning(f"Could not extract text from chunk: {e}")
                        continue
                return # Success

            except Exception as e:
                attempt += 1
                err_msg = str(e)
                
                if "404" in err_msg and self.model_name != "gemini-1.5-flash-latest":
                    logger.warning(f"Model {self.model_name} not found, falling back to 1.5-flash")
                    self.model_name = "gemini-1.5-flash-latest"
                    attempt = 0
                    continue

                if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_attempts:
                    import re
                    delay = base_delay * (2 ** (attempt - 1))
                    match = re.search(r"retry in ([\d\.]+)s", err_msg)
                    if match:
                        try:
                            delay = max(delay, float(match.group(1)) + 1.0)
                        except ValueError: pass
                    
                    logger.warning(f"Gemini Stream rate limited. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Gemini Stream Error: {err_msg}")
                    yield f"Error: {err_msg}"
                    return

class HuggingFaceProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "microsoft/DialoGPT-medium"):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.model_name = model_name
        self.client = InferenceClient(token=self.api_key) if InferenceClient else None
        
    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return "Error: Hugging Face client not initialized"
            
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            response = await asyncio.to_thread(
                self.client.text_generation,
                prompt=full_prompt,
                model=self.model_name,
                max_new_tokens=512,
                temperature=0.7,
                stream=False
            )
            return response
        except Exception as e:
            logger.error(f"Hugging Face Error: {e}")
            return f"Error: {e}"
    
    async def generate_response_stream(self, prompt: str, system_prompt: str):
        if not self.client:
            yield "Error: Hugging Face client not initialized"
            return
            
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            # Use text_generation with stream=True
            def get_stream():
                return self.client.text_generation(
                    prompt=full_prompt,
                    model=self.model_name,
                    max_new_tokens=512,
                    temperature=0.7,
                    stream=True
                )
            
            stream = await asyncio.to_thread(get_stream)
            
            async def async_generator():
                for chunk in stream:
                    if hasattr(chunk, 'token') and hasattr(chunk.token, 'text'):
                        yield chunk.token.text
                    elif hasattr(chunk, 'generated_text'):
                        yield chunk.generated_text
                    elif isinstance(chunk, str):
                        yield chunk
            
            async for token in async_generator():
                if token:
                    yield token
                    
        except Exception as e:
            logger.error(f"Hugging Face Stream Error: {e}")
            yield f"Error: {e}"

class ElevenLabsTTSProvider:
    def __init__(self, api_key: Optional[str] = None, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = voice_id
        self.client = ElevenLabs(api_key=self.api_key) if ElevenLabs else None
        
    async def generate_speech_stream(self, text: str):
        if not self.client:
            logger.error("ElevenLabs client not initialized")
            return
            
        try:
            audio_stream = await asyncio.to_thread(
                self.client.generate,
                text=text,
                voice=Voice(
                    voice_id=self.voice_id,
                    settings=VoiceSettings(stability=0.71, similarity_boost=0.5)
                ),
                stream=True
            )
            
            for chunk in audio_stream:
                yield chunk
        except Exception as e:
            logger.error(f"ElevenLabs TTS Error: {e}")

def get_llm_provider(settings: Settings) -> LLMProvider:
    provider_type = getattr(settings, 'llm_provider', 'gemini').lower()
    
    if provider_type == 'huggingface':
        api_key = getattr(settings, 'huggingface_api_key', None)
        model_name = getattr(settings, 'llm_model', 'microsoft/DialoGPT-medium')
        return HuggingFaceProvider(api_key=api_key, model_name=model_name)
    
    # Default to Gemini
    api_key = settings.google_api_key
    model_name = settings.llm_model
    return GeminiProvider(
        api_key=api_key,
        model_name=model_name,
        project_id=settings.project_id,
        location=settings.location,
    )

def get_tts_provider(settings: Settings):
    tts_provider = getattr(settings, 'tts_provider', 'google').lower()
    
    if tts_provider == 'elevenlabs':
        api_key = getattr(settings, 'elevenlabs_api_key', None)
        voice_id = getattr(settings, 'elevenlabs_voice_id', '21m00Tcm4TlvDq8ikWAM')
        return ElevenLabsTTSProvider(api_key=api_key, voice_id=voice_id)
    
    # Return None for Google TTS (handled elsewhere)
    return None
