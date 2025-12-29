# backend/test_google_tools.py
import asyncio
import os
import sys

# Add the current directory to sys.path so we can import from api and utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.llm_integration import generate_response, generate_image, vertex_ready
from utils.google_utils import get_credentials

async def main():
    print("--- Testing Google Credentials ---")
    creds = get_credentials()
    if creds:
        print(f"Credentials found and loaded successfully. Project: {getattr(creds, 'project_id', 'unknown')}")
    else:
        print("FAILED to load credentials.")

    print(f"\n--- Testing Vertex AI Status ---")
    print(f"Vertex Ready: {vertex_ready}")

    print("\n--- Testing Gemini (via Vertex AI) ---")
    try:
        # Forcing Gemini 2.0 Flash
        os.environ["LLM_MODEL"] = "gemini-2.0-flash"
        response = await generate_response("Hello DELTA, explain the Darcy's Law briefly using Gemini 2.0 Flash.", role="DELTA")
        print(f"Gemini Response: {response[:200]}...")
    except Exception as e:
        print(f"Gemini Call FAILED: {e}")

    print("\n--- Testing Vertex AI (Imagen) ---")
    try:
        image_url = await generate_image("A scientific diagram of groundwater flow.")
        if image_url:
            print(f"Image generated successfully. URL length: {len(image_url)}")
        else:
            print("Image generation returned None.")
    except Exception as e:
        print(f"Image generation FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())