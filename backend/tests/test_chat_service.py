import pytest
pytest.importorskip("sqlalchemy")

from unittest.mock import MagicMock, AsyncMock, patch
from backend.api.services.chat_service import ChatService
from sqlalchemy.orm import Session

async def _async_stream(chunks):
    for chunk in chunks:
        yield chunk

@pytest.mark.asyncio
async def test_process_user_input_no_conversation():
    db = MagicMock(spec=Session)
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    db.query.return_value.filter.return_value.first.return_value = None

    chat_service = ChatService()
    llm_response, error = await chat_service.process_user_input(db, "Hi", 123)

    assert llm_response is None
    assert error == "Conversation not found"

@pytest.mark.asyncio
async def test_get_conversation_summary_empty():
    db = MagicMock(spec=Session)
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    chat_service = ChatService()
    summary = await chat_service.get_conversation_summary(db, 123)

    assert summary is None


@pytest.mark.asyncio
async def test_process_user_input_tool_call_roundtrip():
    db = MagicMock(spec=Session)
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None
    db.query.return_value.filter.return_value.first.return_value = MagicMock()
    db.query.return_value.filter.return_value.scalar.return_value = 0

    tool_call_response = {
        "text": "Running model.",
        "function_calls": [{"name": "run_model", "args": {"model": "SUMMA"}}],
    }

    llm_service_mock = MagicMock()
    llm_service_mock.generate_response = AsyncMock(side_effect=[tool_call_response, "Done"])

    chat_service = ChatService(llm_service=llm_service_mock)

    with patch.object(chat_service, "get_recent_history", return_value=[]), \
         patch.object(chat_service, "create_message") as create_message_mock, \
         patch("backend.api.services.chat_service.run_tools", return_value=[{"name": "run_model", "result": "ok"}]) :
        response, error = await chat_service.process_user_input(
            db, "Run model", 101, background_tasks=MagicMock()
        )

    assert error is None
    assert response == "Done"
    assert create_message_mock.call_count == 2


@pytest.mark.asyncio
async def test_process_user_input_stream_persists_messages():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = MagicMock()
    db.query.return_value.filter.return_value.scalar.return_value = 0

    llm_service_mock = MagicMock()
    llm_service_mock.generate_stream = lambda *_args, **_kwargs: _async_stream(
        ["chunk-a", "chunk-b"]
    )

    chat_service = ChatService(llm_service=llm_service_mock)

    with patch.object(chat_service, "get_recent_history", return_value=[]), \
         patch.object(chat_service, "create_message") as create_message_mock:
        chunks = []
        async for chunk in chat_service.process_user_input_stream(db, "Hi", 101):
            chunks.append(chunk)

    assert "".join(chunks) == "data: chunk-a\n\ndata: chunk-b\n\n"
    assert create_message_mock.call_count == 2
    assert db.commit.call_count == 2


@pytest.mark.asyncio
async def test_process_user_input_stream_fails_on_user_save():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = MagicMock()
    db.query.return_value.filter.return_value.scalar.return_value = 0

    llm_service_mock = MagicMock()
    llm_service_mock.generate_stream = lambda *_args, **_kwargs: _async_stream(["chunk"])

    chat_service = ChatService(llm_service=llm_service_mock)

    def raise_on_first(*_args, **_kwargs):
        raise RuntimeError("db fail")

    with patch.object(chat_service, "get_recent_history", return_value=[]), \
         patch.object(chat_service, "create_message", side_effect=raise_on_first):
        chunks = []
        async for chunk in chat_service.process_user_input_stream(db, "Hi", 101):
            chunks.append(chunk)

    assert chunks == ["data: Error: Failed to save user message.\n\n"]