from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from .models import Base, User as DBUser
from dotenv import load_dotenv
import os
import bcrypt
import httpx
from .routes import router as api_router



app = FastAPI(title="DELTA Orchestrator")

# Configure CORS
origins = [
    "delta-h-frontend-b338f294b004.herokuapp.com",  # Your frontend's URL
    "http://localhost:5173",  # For local development
    "http://localhost:4173",
    "http://localhost:14525",
    "http://172.17.50.178:14525",
    "http://172.18.61.98:11118",
    "http://172.17.98.82:17568"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://delta-h-frontend-b338f294b004.herokuapp.com"],  # Be specific with the origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


load_dotenv()

# Include the API router with the /api prefix
app.include_router(api_router, prefix="/api")

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

@app.options("/{full_path:path}")
async def handle_options_request(request: Request, full_path: str):
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*", # Update this to "*" if you want to allow all origins
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400"
    })


@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}