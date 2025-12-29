#!/usr/bin/env python3
"""
Script to help set up Google API credentials for DELTA.
"""

import os
import sys

def main():
    print("🔧 DELTA Google API Setup")
    print("=" * 40)
    
    # Check current credentials
    print("\n1. Checking current Google credentials...")
    
    creds_file = "google-credentials.json"
    if os.path.exists(creds_file):
        print(f"✅ Service account file found: {creds_file}")
    else:
        print(f"❌ Service account file not found: {creds_file}")
        return
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    project_id = os.environ.get('PROJECT_ID')
    location = os.environ.get('LOCATION')
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    
    print(f"✅ PROJECT_ID: {project_id}")
    print(f"✅ LOCATION: {location}")
    print(f"{'✅' if google_api_key else '❌'} GOOGLE_API_KEY: {'SET' if google_api_key else 'NOT SET'}")
    
    if not google_api_key:
        print("\n🔑 To get a free Google API key:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Add it to your .env file: GOOGLE_API_KEY=your_key_here")
        print("4. Or set it now:")
        
        api_key = input("Enter your Google API key (or press Enter to skip): ").strip()
        if api_key:
            # Update .env file
            with open('.env', 'r') as f:
                content = f.read()
            
            if 'GOOGLE_API_KEY=' in content:
                # Replace existing
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('GOOGLE_API_KEY='):
                        lines[i] = f'GOOGLE_API_KEY={api_key}'
                        break
                content = '\n'.join(lines)
            else:
                # Add new
                content += f'\nGOOGLE_API_KEY={api_key}\n'
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ API key saved to .env file")
    
    print("\n🧪 Testing services...")
    
    # Test TTS
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file
        from utils.google_utils import get_tts_client
        client = get_tts_client()
        print("✅ Google TTS: Working")
    except Exception as e:
        print(f"❌ Google TTS: {e}")
    
    # Test free Gemini API
    if google_api_key or os.environ.get('GOOGLE_API_KEY'):
        try:
            import google.genai as genai
            genai.configure(api_key=google_api_key or os.environ.get('GOOGLE_API_KEY'))
            client = genai.Client()
            print("✅ Free Gemini API: Working")
        except Exception as e:
            print(f"❌ Free Gemini API: {e}")
    
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    main()
