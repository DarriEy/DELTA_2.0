from fastapi import APIRouter, Request, Depends
from utils.config import get_settings
import os

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "DELTA Backend is running"}

@router.get("/debug/config")
async def debug_config():
    settings = get_settings()
    return {
        "PROJECT_ID": settings.project_id,
        "LOCATION": settings.location,
        "GOOGLE_API_KEY_SET": bool(settings.google_api_key),
        "MODE": "stateless"
    }
