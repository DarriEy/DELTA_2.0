import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from backend.utils.error_handlers import register_exception_handlers, DeltaError, ValidationError

def test_delta_error_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/error")
    async def trigger_error():
        raise DeltaError("Custom delta error", status_code=418, error_code="TEAPOT")

    client = TestClient(app)
    response = client.get("/error")
    
    assert response.status_code == 418
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Custom delta error"
    assert data["error_code"] == "TEAPOT"

def test_validation_error_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/validation")
    async def trigger_validation():
        raise ValidationError("Missing field")

    client = TestClient(app)
    response = client.get("/validation")
    
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"

def test_http_exception_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/http")
    async def trigger_http():
        raise HTTPException(status_code=403, detail="Forbidden access")

    client = TestClient(app)
    response = client.get("/http")
    
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "HTTP_403"
    assert data["message"] == "Forbidden access"

def test_unhandled_exception_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/unhandled")
    async def trigger_unhandled():
        raise RuntimeError("Something went wrong")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/unhandled")
    
    assert response.status_code == 500
    data = response.json()
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    assert data["message"] == "An internal server error occurred."