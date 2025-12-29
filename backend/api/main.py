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
    raise ValueError("DATABASE_URL environment variable is not set!")

DATABASE_URL = raw_db_url.replace(
    "postgres://", "postgresql://", 1
)

# Sync engine and session
# Add timeout to prevent hanging if DB is unreachable
engine = create_engine(DATABASE_URL, echo=False, connect_args={"connect_timeout": 10})

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
        print(f"An error occurred during user creation: {e}")
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/google-credentials.json"
    print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    print("DELTA Backend Started")

    # Create tables if they don't exist
    try:
        print("Attempting to connect to database...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        # Create initial user
        create_initial_user()
    except Exception as e:
        # Catch DB errors so the app still starts and we can see logs
        print(f"CRITICAL ERROR: Failed to connect to database or create tables: {e}")
        # We do NOT raise here, so the app can still serve /health


# Include the API router with the /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}