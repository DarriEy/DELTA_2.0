from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Message as DBMessage, Conversation as DBConversation
from .llm_service import get_llm_service
import logging
from typing import List, Dict, Any, Union, Optional, Tuple
try:
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover - optional dependency for tests
    class BackgroundTasks:  # type: ignore[no-redef]
        pass
from .tool_runner import run_tools

log = logging.getLogger(__name__)

def parse_llm_response(llm_response: Union[str, Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    if isinstance(llm_response, dict) and "function_calls" in llm_response:
        return llm_response.get("text", ""), llm_response.get("function_calls", [])
    return str(llm_response), []

def create_message(db: Session, content: str, sender: str, conversation_id: int, message_index: int):
    db_message = DBMessage(
        content=str(content),
        sender=sender,
        conversation_id=conversation_id,
        message_index=message_index,
    )
    db.add(db_message)
    return db_message

def get_recent_history(db: Session, conversation_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves recent messages for context."""
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index.desc())
        .limit(limit)
        .all()
    )
    # Reverse to chronological order
    messages.reverse()
    
    return [
        {"role": "user" if msg.sender == "user" else "model", "content": msg.content}
        for msg in messages
    ]

async def _prepare_conversation_turn(
    db: Session, user_input: str, conversation_id: int
) -> Tuple[Optional[DBConversation], Optional[List[Dict[str, Any]]], int, Optional[str]]:
    conversation = db.query(DBConversation).filter(
        DBConversation.id == conversation_id
    ).first()

    if not conversation:
        return None, None, 0, "Conversation not found"

    # Fetch history BEFORE adding the new message
    history = get_recent_history(db, conversation_id)

    last_message_index = (
        db.query(func.max(DBMessage.message_index))
        .filter(DBMessage.conversation_id == conversation_id)
        .scalar()
    ) or 0

    return conversation, history, last_message_index, None

async def process_user_input(
    db: Session, 
    user_input: str, 
    conversation_id: int, 
    background_tasks: Optional[BackgroundTasks] = None
):
    _, history, last_message_index, error = await _prepare_conversation_turn(
        db, user_input, conversation_id
    )
    if error:
        return None, error

    # Generate LLM response (first turn)
    llm_service = get_llm_service()
    llm_response = await llm_service.generate_response(user_input, history=history)
    text_part, function_calls = parse_llm_response(llm_response)

    final_text_response: Union[str, Dict[str, Any]] = text_part

    if function_calls:
        current_history = history.copy()
        current_history.append({"role": "user", "content": user_input})
        current_history.append({"role": "model", "content": text_part})

        tool_results = run_tools(db, background_tasks, function_calls)
        tool_feedback = "\n".join(
            [f"Tool '{item['name']}' Output: {item['result']}" for item in tool_results]
        )

        final_text_response = await llm_service.generate_response(
            tool_feedback,
            history=current_history,
        )

        if isinstance(final_text_response, dict):
            final_text_response = final_text_response.get("text", "Tool executed.")

    try:
        create_message(db, user_input, "user", conversation_id, last_message_index + 1)
        create_message(
            db,
            final_text_response,
            "assistant",
            conversation_id,
            last_message_index + 2,
        )
        db.commit()
    except Exception as exc:
        log.error("Failed to persist conversation messages: %s", exc)
        db.rollback()
        return None, "Failed to save conversation messages."

    return final_text_response, None

async def process_user_input_stream(db: Session, user_input: str, conversation_id: int):
    _, history, last_message_index, error = await _prepare_conversation_turn(
        db, user_input, conversation_id
    )
    if error:
        yield f"Error: {error}"
        return

    try:
        create_message(db, user_input, "user", conversation_id, last_message_index + 1)
        db.commit()
    except Exception as exc:
        log.error("Failed to persist user message: %s", exc)
        db.rollback()
        yield "Error: Failed to save user message."
        return

    full_response = ""
    llm_service = get_llm_service()
    async for chunk in llm_service.generate_stream(user_input, history=history):
        full_response += chunk
        yield chunk

    try:
        create_message(db, full_response, "assistant", conversation_id, last_message_index + 2)
        db.commit()
    except Exception as exc:
        log.error("Failed to persist assistant message: %s", exc)
        db.rollback()
        yield "Error: Failed to save assistant message."

async def get_conversation_summary(db: Session, conversation_id: int):
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index)
        .all()
    )

    if not messages:
        return None

    formatted_messages = [
        {"sender": msg.sender, "content": msg.content} for msg in messages
    ]

    return await get_llm_service().generate_summary_from_messages(formatted_messages)
