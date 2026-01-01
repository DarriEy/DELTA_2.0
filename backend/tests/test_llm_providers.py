import pytest

pytest.importorskip("google.genai")

from backend.api.llm_providers import GeminiProvider


class DummyChunk:
    def __init__(self, text):
        self.text = text


class DummyAioModels:
    def __init__(self, stream_factory):
        self._stream_factory = stream_factory

    def generate_content_stream(self, **_kwargs):
        return self._stream_factory()


class DummyAio:
    def __init__(self, stream_factory):
        self.models = DummyAioModels(stream_factory)


class DummyClient:
    def __init__(self, stream_factory):
        self.aio = DummyAio(stream_factory)


@pytest.mark.asyncio
async def test_gemini_stream_handles_awaitable(monkeypatch):
    async def stream_generator():
        yield DummyChunk("chunk-1")
        yield DummyChunk("chunk-2")

    async def stream_factory():
        return stream_generator()

    def dummy_client_factory(*_args, **_kwargs):
        return DummyClient(stream_factory)

    monkeypatch.setattr(
        "backend.api.llm_providers.genai.Client",
        dummy_client_factory,
    )

    provider = GeminiProvider(api_key="test", model_name="test")
    chunks = []
    async for chunk in provider.generate_response_stream_with_history(
        "prompt", "system", []
    ):
        chunks.append(chunk)

    assert chunks == ["chunk-1", "chunk-2"]
