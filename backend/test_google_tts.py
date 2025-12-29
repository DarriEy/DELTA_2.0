# backend/test_google_tts.py
import asyncio
import os
import sys

# Add the current directory to sys.path so we can import from api and utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.google_utils import get_tts_client, get_credentials
from google.cloud import texttospeech

async def main():
    print("--- Testing Google TTS ---")
    try:
        creds = get_credentials()
        print(f"Using credentials for: {getattr(creds, 'project_id', 'unknown')}")
        
        client = get_tts_client()
        synthesis_input = texttospeech.SynthesisInput(text="Hello, I am DELTA. Your hydrological assistant is online.")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Polyglot-1"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        print(f"TTS Success! Audio length: {len(response.audio_content)} bytes")
    except Exception as e:
        print(f"TTS FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
