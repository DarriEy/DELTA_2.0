#!/usr/bin/env python3
"""
Test if DELTA backend is deployed and working
"""

import requests
import time
import json

BACKEND_URL = "https://delta-backend-zom0.onrender.com"

def test_backend():
    print("🧪 Testing DELTA Backend Deployment")
    print("=" * 40)
    
    # Test 1: Health check
    print(f"\n1. Testing backend health at {BACKEND_URL}...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responding")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        return False
    
    # Test 2: TTS endpoint
    print("\n2. Testing TTS endpoint...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/tts",
            json={"text": "Hello, I am DELTA!"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if "audioContent" in data:
                print("✅ TTS endpoint working")
            else:
                print("❌ TTS endpoint not returning audio")
        else:
            print(f"❌ TTS endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ TTS endpoint failed: {e}")
    
    # Test 3: Chat endpoint
    print("\n3. Testing chat endpoint...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/learn",
            json={"user_input": "Hello DELTA, say hi!"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ Chat endpoint working")
                print(f"   Response: {data['response'][:50]}...")
            else:
                print("❌ Chat endpoint not returning response")
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
    
    print(f"\n🎉 Backend test complete!")
    print(f"🌐 Frontend should now work at: https://darriey.github.io/DELTA_2.0/")
    return True

if __name__ == "__main__":
    print("⏳ Waiting for deployment to complete...")
    time.sleep(30)  # Give deployment time to start
    
    for attempt in range(5):
        print(f"\n🔄 Attempt {attempt + 1}/5")
        if test_backend():
            break
        if attempt < 4:
            print("⏳ Waiting 30 seconds before retry...")
            time.sleep(30)
    else:
        print("\n❌ Backend deployment may have failed. Check Render dashboard.")
