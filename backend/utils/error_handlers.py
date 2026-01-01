import logging
from typing import Optional, Any, Dict

try:
    from fastapi import Request, HTTPException, status
    from fastapi.responses import JSONResponse
    from api.schemas import APIResponse
except ImportError:
    Request = HTTPException = status = JSONResponse = object
    APIResponse = None

log = logging.getLogger(__name__)

class DeltaError(Exception):
    """Base class for DELTA-specific errors."""
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ValidationError(DeltaError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")

class NotFoundError(DeltaError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")

class ExternalServiceError(DeltaError):
    def __init__(self, service_name: str, detail: str):
        super().__init__(
            f"Error from external service '{service_name}': {detail}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR"
        )

class AuthenticationError(DeltaError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_FAILED")

def register_exception_handlers(app, logger=None) -> None:
    current_log = logger or log

    @app.exception_handler(DeltaError)
    async def delta_exception_handler(request: Request, exc: DeltaError):
        current_log.error(f"DeltaError [{exc.error_code}]: {exc.message}")
        content = {
            "status": "error",
            "message": exc.message,
            "error_code": exc.error_code
        }
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        current_log.warning("HTTPException: %s", exc.detail)
        content = {
            "status": "error",
            "message": str(exc.detail),
            "error_code": f"HTTP_{exc.status_code}"
        }
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        current_log.exception("Unhandled exception")
        content = {
            "status": "error",
            "message": "An internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
        # If in debug/dev, we might want to include more info, but usually best to hide details
        return JSONResponse(status_code=500, content=content)