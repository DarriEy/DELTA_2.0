# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from api.models import Base, User as DBUser, engine, async_session
from dotenv import load_dotenv
import os
import bcrypt
import httpx
from api.routes import router as api_router


load_dotenv()

app = FastAPI(title="DELTA Orchestrator")

# Configure CORS
origins = [
    "http://localhost:5173",  # Allow your frontend's origin
    "http://localhost:4173",
    # Add other origins if needed, such as a production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific methods like ["GET", "POST"]
    allow_headers=["*"],  # You can specify specific headers
)

# Database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# Async engine and session
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_initial_user():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(DBUser).where(DBUser.user_id == 1))
            user_exists = result.scalar_one_or_none()

            if not user_exists:
                hashed_password = bcrypt.hashpw(
                    "testpassword".encode("utf-8"),  # Replace with a secure password
                    bcrypt.gensalt(),
                ).decode("utf-8")

                db_user = DBUser(
                    user_id=1,
                    username="testuser",
                    email="testuser@example.com",
                    password_hash=hashed_password,
                )
                session.add(db_user)
                await session.commit()
                print("User with ID 1 created.")
            else:
                print("User with ID 1 already exists.")


@app.on_event("startup")
async def startup_event():
    app.state.httpx_client = httpx.AsyncClient()
    print("DELTA Backend Started")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create initial user
    await create_initial_user()


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.httpx_client.aclose()


app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)