import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .models import Base
from .routers import chat, jobs, users
from utils.db import get_engine, get_session_local
from utils.config import get_settings
from utils.settings import load_environment
from utils.logging_config import setup_logging
from utils.error_handlers import register_exception_handlers

def create_app() -> FastAPI:
    load_environment()
    setup_logging()
    log = logging.getLogger(__name__)

    engine = get_engine()
    session_local = get_session_local()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        log.info("DELTA Backend Starting...")
        from .llm_integration import init_vertex
        init_vertex()

        creds_path = "/app/google-credentials.json"
        if os.path.exists(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            log.info("Using Google credentials from %s", creds_path)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            log.info(
                "Using Google credentials from environment path: %s",
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            )
        else:
            log.warning("GOOGLE_APPLICATION_CREDENTIALS not set. Google Cloud features will fail.")

        if session_local and engine:
            try:
                log.info("Attempting to connect to database...")
                Base.metadata.create_all(bind=engine)
                log.info("Tables created successfully.")
                create_initial_user(session_local)
            except Exception as e:
                log.error("Failed to connect to database: %s", e)
        else:
            log.warning("Skipping database initialization (no SessionLocal)")

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

    # Add this OPTIONS handler before including the router
    @app.options("/{full_path:path}")
    async def handle_options_request(request: Request, full_path: str):
        origin = request.headers.get("Origin")
        # Dynamically allow the origin if it's in our allowed list
        allow_origin = origin if origin in origins else (origins[0] if origins else "*")

        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, PATCH, DELETE", 
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        })

    if not os.environ.get("DATABASE_URL"):
        log.warning("DATABASE_URL environment variable is not set! Database features will fail.")

    def create_initial_user(session_factory):
        if not session_factory:
            return
        db = session_factory()
        try:
            # Simple placeholder for initial user creation
            pass
        finally:
            db.close()
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(jobs.router, prefix="/api", tags=["jobs"])
    app.include_router(users.router, prefix="/api", tags=["users"])
    
    # Add health check router
    from .routers.health import router as health_router
    app.include_router(health_router, prefix="/api", tags=["health"])

    @app.get("/api/health/google")
    async def google_health_check():
        """Checks the status of Google service integration."""
        from .services.health_service import get_health_service
        return await get_health_service().check_google_health()

    @app.get("/api/debug/config")
    async def debug_config():
        return {
            "PROJECT_ID": settings.project_id,
            "LOCATION": settings.location,
            "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            "GOOGLE_API_KEY_SET": bool(settings.google_api_key),
            "DATABASE_URL_SET": bool(os.environ.get("DATABASE_URL")),
        }

    @app.get("/")
    async def root():
        return {"message": "DELTA Backend Started"}

    return app


app = create_app()
