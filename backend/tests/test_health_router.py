"""Tests for health check router."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_health_endpoint_exists(client):
    """Test that health endpoint is accessible."""
    response = client.get("/api/health")
    assert response.status_code == 200


@patch('api.routers.health.APIClientFactory.health_check_all')
def test_health_check_all_healthy(mock_health_check, client):
    """Test health check when all services are healthy."""
    mock_health_check.return_value = {"llm": True, "tts": True}
    
    response = client.get("/api/health")
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["services"] == {"llm": True, "tts": True}


@patch('api.routers.health.APIClientFactory.health_check_all')
def test_health_check_degraded(mock_health_check, client):
    """Test health check when some services are down."""
    mock_health_check.return_value = {"llm": True, "tts": False}
    
    response = client.get("/api/health")
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "degraded"
    assert data["services"] == {"llm": True, "tts": False}


@patch('api.routers.health.APIClientFactory.health_check_all')
def test_health_check_handles_exception(mock_health_check, client):
    """Test health check handles exceptions gracefully."""
    mock_health_check.side_effect = Exception("Service unavailable")
    
    response = client.get("/api/health")
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "unhealthy"
    assert "error" in data
