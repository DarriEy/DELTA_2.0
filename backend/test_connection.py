import asyncio
import asyncpg
import os

async def test_connection():
    database_url = os.environ.get("DATABASE_URL")
    print(f"Attempting to connect to: {database_url}")

    try:
        conn = await asyncpg.connect(database_url)
        print("Connection successful!")
        await conn.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
