import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000"

async def test_integration():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔍 Testing Health Check...")
        try:
            resp = await client.get(f"{BASE_URL}/api/health")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except Exception as e:
            print(f"❌ Backend not reachable at {BASE_URL}. Ensure it is running.")
            return

        print("\n🔍 Testing User Creation...")
        import random
        email = f"test_{random.randint(0, 10000)}@example.com"
        user_data = {"username": "testuser", "email": email, "password": "password123"}
        resp = await client.post(f"{BASE_URL}/api/users/", json=user_data)
        if resp.status_code in [200, 201]:
            user = resp.json()
            user_id = user["user_id"]
            print(f"✅ User created with ID: {user_id}")
        else:
            print(f"❌ User creation failed: {resp.text}")
            return

        print("\n🔍 Testing Conversation Creation...")
        conv_data = {"active_mode": "general", "user_id": user_id}
        resp = await client.post(f"{BASE_URL}/api/conversations/", json=conv_data)
        if resp.status_code in [200, 201]:
            conv = resp.json()
            conv_id = conv["conversation_id"]
            print(f"✅ Conversation created with ID: {conv_id}")
        else:
            print(f"❌ Conversation creation failed: {resp.text}")
            return

        print("\n🔍 Testing Chat Process...")
        chat_data = {"user_input": "What is the water cycle?", "conversation_id": conv_id}
        resp = await client.post(f"{BASE_URL}/api/process", json=chat_data)
        if resp.status_code == 200:
            print(f"✅ Chat processed. Response: {resp.json()['llmResponse'][:100]}...")
        else:
            print(f"❌ Chat process failed: {resp.text}")

        print("\n🔍 Testing Summary Generation...")
        resp = await client.get(f"{BASE_URL}/api/summary/{conv_id}")
        if resp.status_code == 200:
            print(f"✅ Summary generated: {resp.json()['summary'][:100]}...")
        else:
            print(f"❌ Summary generation failed: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_integration())
