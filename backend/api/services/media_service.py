import base64
from typing import Dict, Optional

from fastapi import HTTPException
from google.cloud import texttospeech

from utils.google_utils import get_tts_client
from .llm_service import get_llm_service


class MediaService:
    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm_service = llm_service or get_llm_service()

    async def generate_image_data_uri(self, prompt: str) -> str:
        data_uri = await self.llm_service.generate_image(prompt)
        if not data_uri:
            raise HTTPException(status_code=500, detail="Image generation failed")
        return data_uri

    def synthesize_speech(self, text: str) -> Dict[str, str]:
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        tts_client = get_tts_client()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Polyglot-1"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_content = base64.b64encode(response.audio_content).decode("utf-8")
        return {"audioContent": audio_content}

_SERVICE: Optional[MediaService] = None

def get_media_service() -> MediaService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MediaService()
    return _SERVICE