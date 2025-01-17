from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from .models import Base, User as DBUser
from dotenv import load_dotenv
import os
import bcrypt
import httpx
from .routes import router as api_router

load_dotenv()

app = FastAPI(title="DELTA Orchestrator")

# Configure CORS
origins = [
    "https://delta-h-7344a1b27b42.herokuapp.com",  # Your frontend URL
    "http://localhost:5173",  # For local development
    "http://localhost:4173",
    "http://localhost:14525",
    "http://172.17.50.178:14525",
    "http://172.18.61.98:11118",
    "http://172.17.98.82:17568"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)

# Sync engine and session
engine = create_engine(DATABASE_URL, echo=False)

# Use Session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_initial_user():
    db = SessionLocal()
    try:
        user_exists = db.query(DBUser).filter(DBUser.user_id == 1).first()

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
            db.add(db_user)
            db.commit()
            print("User with ID 1 created.")
        else:
            print("User with ID 1 already exists.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    app.state.httpx_client = httpx.AsyncClient()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/google-credentials.json"
    print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    print("DELTA Backend Started")

    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")
        raise

    # Create initial user
    create_initial_user()


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.httpx_client.aclose()


# Include the API router with the /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}