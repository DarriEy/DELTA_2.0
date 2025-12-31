import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.api.services import chat_service
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_process_user_input_no_conversation():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None

    llm_response, error = await chat_service.process_user_input(db, "Hi", 123)

    assert llm_response is None
    assert error == "Conversation not found"

@pytest.mark.asyncio
async def test_get_conversation_summary_empty():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    summary = await chat_service.get_conversation_summary(db, 123)

    assert summary is None
