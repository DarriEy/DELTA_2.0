"""Health check endpoint for monitoring service status."""

from fastapi import APIRouter
from typing import Dict, Any
import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check for stateless mode."""
    return {
        "status": "healthy",
        "mode": "stateless",
        "timestamp": datetime.datetime.now().isoformat()
    }