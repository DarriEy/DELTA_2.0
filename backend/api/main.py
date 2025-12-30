import os

import bcrypt
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Base, User as DBUser
from .routes import router as api_router

load_dotenv()

# Also load from secure home directory env file
import os
home_env_path = os.path.expanduser("~/.env_delta")
if os.path.exists(home_env_path):
    load_dotenv(home_env_path)

app = FastAPI(title="DELTA Orchestrator")

# Configure CORS
origins = [
    "https://delta-h-frontend-b338f294b004.herokuapp.com",  # Your frontend's URL
    "https://darriey.github.io",
    "https://DarriEy.github.io",
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
    allow_methods=["*"],  # Allows all methods, including PUT
    allow_headers=["*"],  # Allows all headers
)

# Add this OPTIONS handler before including the router
@app.options("/{full_path:path}")
async def handle_options_request(request: Request, full_path: str):
    origin = request.headers.get("Origin")
    # Dynamically allow the origin if it's from github.io or localhost
    allow_origin = origin if origin and ("github.io" in origin or "localhost" in origin) else "https://DarriEy.github.io"

    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, PATCH, DELETE", 
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400"
    })

# Database URL from environment variable
raw_db_url = os.environ.get("DATABASE_URL")
if not raw_db_url:
    print("WARNING: DATABASE_URL environment variable is not set! Database features will fail.")
    DATABASE_URL = "sqlite:///./fallback.db" # Use a dummy fallback to prevent crash
else:
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)

# Sync engine and session
# Add timeout to prevent hanging if DB is unreachable
try:
    if "postgresql" in DATABASE_URL:
        # For PostgreSQL, connect_timeout is passed in connect_args
        engine = create_engine(DATABASE_URL, echo=False, connect_args={"connect_timeout": 10})
    else:
        # For SQLite or others, connect_timeout might not be supported or named differently
        engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Failed to create engine: {e}")
    SessionLocal = None


def get_db():
    if not SessionLocal:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_initial_user():
    if not SessionLocal: return
    db = SessionLocal()
    try:
        # Simple placeholder for initial user creation
        pass
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print("DELTA Backend Starting...")
    
    # Robust credential handling
    creds_path = "/app/google-credentials.json"
    if os.path.exists(creds_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        print(f"Using Google credentials from {creds_path}")
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print(f"Using Google credentials from environment path: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    else:
        print("WARNING: GOOGLE_APPLICATION_CREDENTIALS not set. Google Cloud features will fail.")

    if SessionLocal:
        # Create tables if they don't exist
        try:
            print("Attempting to connect to database...")
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
            
            # Create initial user
            create_initial_user()
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to connect to database: {e}")
    else:
        print("Skipping database initialization (no SessionLocal)")

@app.get("/health/google")
async def google_health_check():
    """Checks the status of Google service integration."""
    results = {
        "generative_ai": "unknown",
        "vertex_ai": "unknown",
        "credentials_found": os.path.exists(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")),
    }
    
    try:
        import google.generativeai as genai
        from .llm_integration import GOOGLE_API_KEY
        if GOOGLE_API_KEY:
            # Quick test of the API
            model = genai.GenerativeModel('gemini-1.5-flash')
            results["generative_ai"] = "ok"
        else:
            results["generative_ai"] = "missing_api_key"
    except Exception as e:
        results["generative_ai"] = f"error: {str(e)}"

    return results


# Include the API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}