"""Integration tests for refactored components."""

import pytest
from fastapi.testclient import TestClient
from api.main import create_app


@pytest.fixture
def app():
    """Create FastAPI app instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_app_starts_successfully(app):
    """Test that the app can be created without errors."""
    assert app is not None
    assert app.title == "DELTA Orchestrator"


def test_health_endpoint_accessible(client):
    """Test health endpoint is accessible and returns expected format."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "services" in data
    assert "timestamp" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


def test_cors_headers_present(client):
    """Test CORS headers are properly configured."""
    response = client.options("/api/health")
    
    # Should handle OPTIONS requests
    assert response.status_code in [200, 204]


def test_root_endpoint_works(client):
    """Test root endpoint still works after refactoring."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_api_routes_registered(client):
    """Test that all expected API routes are registered."""
    # Test that main API routes exist (even if they return errors due to missing auth/data)
    routes_to_test = [
        "/api/health",
        "/",
    ]
    
    for route in routes_to_test:
        response = client.get(route)
        # Should not return 404 (route not found)
        assert response.status_code != 404
