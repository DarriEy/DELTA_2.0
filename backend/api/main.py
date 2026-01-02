import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .routers import chat, jobs, users, health, system
from utils.config import get_settings
from utils.settings import load_environment
from utils.logging_config import setup_logging
from utils.error_handlers import register_exception_handlers

def create_app() -> FastAPI:
    load_environment()
    setup_logging()
    log = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        log.info("DELTA Backend Starting (Stateless Mode)...")
        
        from .services.llm_service import get_llm_service
        get_llm_service().init_vertex()

        yield

    app = FastAPI(title="DELTA Orchestrator", lifespan=lifespan)
    register_exception_handlers(app, log)

    # Configure CORS
    settings = get_settings()
    app.state.settings = settings
    origins = settings.allowed_origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods, including PUT
        allow_headers=["*"],  # Allows all headers
    )

    @app.get("/")
    async def root():
        return {"message": "DELTA backend is running (Stateless)"}

    # Include Routers
    app.include_router(system.router, tags=["system"])
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(jobs.router, prefix="/api", tags=["jobs"])
    app.include_router(users.router, prefix="/api", tags=["users"])
    app.include_router(health.router, prefix="/api", tags=["health"])

    return app


app = create_app()
