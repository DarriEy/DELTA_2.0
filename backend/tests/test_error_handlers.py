import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from backend.utils.error_handlers import register_exception_handlers


def test_register_exception_handlers_registers_handlers():
    app = FastAPI()
    register_exception_handlers(app, app.logger if hasattr(app, "logger") else None)

    assert Exception in app.exception_handlers
    assert HTTPException in app.exception_handlers
