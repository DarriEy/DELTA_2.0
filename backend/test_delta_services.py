#!/usr/bin/env python3
"""
Test script for DELTA's Google services
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_all_services():
    load_dotenv()
    
    print("🧪 Testing DELTA Google Services")
    print("=" * 40)
    
    # Test 1: TTS
    print("\n1. Testing Google Text-to-Speech...")
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-credentials.json'
        from utils.google_utils import get_tts_client
        from google.cloud import texttospeech
        
        client = get_tts_client()
        synthesis_input = texttospeech.SynthesisInput(text="Hello, I am DELTA!")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            name="en-US-Polyglot-1"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        print("✅ TTS: Working (audio length:", len(response.audio_content), "bytes)")
    except Exception as e:
        print("❌ TTS:", str(e))
    
    # Test 2: Gemini API
    print("\n2. Testing Free Gemini API...")
    try:
        from api.llm_integration import generate_response
        response = await generate_response("Say hello in one sentence.", "DELTA")
        if "error" not in response.lower():
            print("✅ Gemini API: Working")
            print("   Response:", response[:100] + "...")
        else:
            print("❌ Gemini API:", response[:100])
    except Exception as e:
        print("❌ Gemini API:", str(e))
    
    # Test 3: Image Generation
    print("\n3. Testing Image Generation...")
    try:
        from api.llm_integration import generate_image
        image_url = await generate_image("A beautiful mountain landscape")
        if image_url and image_url.startswith("data:image"):
            print("✅ Image Generation: Working")
        else:
            print("❌ Image Generation: Failed")
    except Exception as e:
        print("❌ Image Generation:", str(e))
    
    print("\n🎉 Test complete!")
    print("\nTo get a valid Google API key:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Replace the placeholder in .env file")

if __name__ == "__main__":
    asyncio.run(test_all_services())
