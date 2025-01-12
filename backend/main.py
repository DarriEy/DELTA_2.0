# backend/main.py
from fastapi import FastAPI
from api.routes import router as api_router
from utils.config import config
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import httpx

app = FastAPI(title="DELTA Orchestrator")

# Allow CORS for your frontend's origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend's actual origin if it's different
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    app.state.httpx_client = httpx.AsyncClient()
    print("DELTA Backend Started")

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.httpx_client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)