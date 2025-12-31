import pytest
from backend.api.llm_providers import GeminiProvider
from unittest.mock import MagicMock, patch

@pytest.mark.asyncio
async def test_gemini_provider_generate_response():
    # Mock the genai Client
    with patch('google.genai.Client') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_model = mock_client_instance.models
        mock_response = MagicMock()
        mock_response.text = "Hello, I am Gemini"
        mock_model.generate_content.return_value = mock_response

        provider = GeminiProvider(api_key="test_key")
        response = await provider.generate_response("Hi", "You are an assistant")

        assert response == "Hello, I am Gemini"
        mock_model.generate_content.assert_called_once()
