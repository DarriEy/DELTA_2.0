"""Unified API client factory for external services."""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class APIClient(ABC):
    """Base class for all API clients."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the API service is available."""
        pass


class APIClientFactory:
    """Factory for creating and managing API clients."""
    
    _clients: Dict[str, APIClient] = {}
    
    @classmethod
    def get_client(cls, service_name: str, **kwargs) -> APIClient:
        """Get or create an API client for the specified service."""
        if service_name not in cls._clients:
            cls._clients[service_name] = cls._create_client(service_name, **kwargs)
        return cls._clients[service_name]
    
    @classmethod
    def _create_client(cls, service_name: str, **kwargs) -> APIClient:
        """Create a new API client instance."""
        from .llm_providers import get_llm_provider
        from .services.google_services import GoogleTTSService
        
        if service_name == "llm":
            return get_llm_provider()
        elif service_name == "tts":
            return GoogleTTSService()
        else:
            raise ValueError(f"Unknown service: {service_name}")
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """Check health of all registered clients."""
        results = {}
        for name, client in cls._clients.items():
            try:
                results[name] = await client.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        return results
