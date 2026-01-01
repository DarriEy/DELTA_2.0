"""Tests for API client factory."""

import pytest
from unittest.mock import AsyncMock, patch
from api.client_factory import APIClientFactory, APIClient


class MockAPIClient(APIClient):
    async def health_check(self) -> bool:
        return True


@pytest.fixture
def clean_factory():
    """Clean factory state between tests."""
    APIClientFactory._clients.clear()
    yield
    APIClientFactory._clients.clear()


def test_get_client_creates_new_instance(clean_factory):
    """Test that get_client creates new instances."""
    with patch.object(APIClientFactory, '_create_client', return_value=MockAPIClient()):
        client = APIClientFactory.get_client("test_service")
        assert isinstance(client, MockAPIClient)


def test_get_client_reuses_existing_instance(clean_factory):
    """Test that get_client reuses existing instances."""
    with patch.object(APIClientFactory, '_create_client', return_value=MockAPIClient()) as mock_create:
        client1 = APIClientFactory.get_client("test_service")
        client2 = APIClientFactory.get_client("test_service")
        
        assert client1 is client2
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_health_check_all_success(clean_factory):
    """Test health check for all clients."""
    mock_client = MockAPIClient()
    APIClientFactory._clients["test"] = mock_client
    
    results = await APIClientFactory.health_check_all()
    assert results == {"test": True}


@pytest.mark.asyncio
async def test_health_check_all_handles_failure(clean_factory):
    """Test health check handles client failures."""
    mock_client = MockAPIClient()
    mock_client.health_check = AsyncMock(side_effect=Exception("Connection failed"))
    APIClientFactory._clients["test"] = mock_client
    
    results = await APIClientFactory.health_check_all()
    assert results == {"test": False}
