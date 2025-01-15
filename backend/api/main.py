# backend/main.py
from fastapi import FastAPI
from api.routes import router as api_router
from utils.config import config
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import httpx
from .models import create_tables, User, Conversation, Message, ModelConfig, ModelRun, EducationalProgress, get_db, engine


app = FastAPI(title="DELTA Orchestrator")

# Configure CORS
origins = [
    "http://localhost:5173",  # Add your frontend's origin here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    app.state.httpx_client = httpx.AsyncClient()
    print("DELTA Backend Started")

    # Create tables if they don't exist
    await create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.httpx_client.aclose()

@app.get("/")
async def root():
    return {"message": "DELTA Backend Started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)