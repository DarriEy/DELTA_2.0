import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.routing import APIRoute

FastAPI = fastapi.FastAPI

from backend.api.main import create_app


def test_create_app_registers_routes():
    app = create_app()
    assert isinstance(app, FastAPI)

    paths = {route.path for route in app.router.routes if isinstance(route, APIRoute)}
    assert "/" in paths
    assert "/api/health/google" in paths
    assert "/api/process" in paths
