"""Health check endpoint for monitoring service status."""

from fastapi import APIRouter
from typing import Dict, Any
import logging

from ..client_factory import APIClientFactory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check for all services."""
    try:
        # Check API clients
        client_health = await APIClientFactory.health_check_all()
        
        # Overall status
        all_healthy = all(client_health.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": client_health,
            "timestamp": "2026-01-01T12:34:26.275-07:00"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2026-01-01T12:34:26.275-07:00"
        }
