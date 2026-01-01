import logging
from typing import Callable

try:
    from fastapi import Request, HTTPException
    from fastapi.responses import JSONResponse
    from api.schemas import APIResponse
except ImportError:  # pragma: no cover - optional dependency for tests
    Request = HTTPException = JSONResponse = object
    APIResponse = None


def register_exception_handlers(app, logger=None) -> None:
    log = logger or logging.getLogger(__name__)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.exception("Unhandled exception")
        if APIResponse:
            payload = APIResponse(status="error", message=str(exc)).model_dump()
        else:
            payload = {"detail": "An internal server error occurred.", "message": str(exc)}
        return JSONResponse(
            status_code=500,
            content=payload,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.warning("HTTPException: %s", exc.detail)
        if APIResponse:
            payload = APIResponse(status="error", message=str(exc.detail)).model_dump()
        else:
            payload = {"detail": exc.detail}
        return JSONResponse(status_code=exc.status_code, content=payload)
