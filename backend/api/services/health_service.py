import os
import logging
from typing import Optional, Dict, Any
from utils.config import get_settings
from api.llm_integration import generate_response

log = logging.getLogger(__name__)

class HealthService:
    async def check_google_health(self) -> Dict[str, Any]:
        """Checks the status of Google service integration."""
        project_id = get_settings().project_id
        
        results = {
            "generative_ai": "unknown",
            "vertex_ai": "ok" if project_id else "not_configured",
            "credentials_found": os.path.exists(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")),
            "project_id": project_id
        }
        
        try:
            response = await generate_response("health check")
            if "Error" not in response:
                results["generative_ai"] = "ok"
            else:
                results["generative_ai"] = f"error: {response}"
        except Exception as e:
            results["generative_ai"] = f"error: {str(e)}"

        return results

_SERVICE: Optional[HealthService] = None

def get_health_service() -> HealthService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = HealthService()
    return _SERVICE