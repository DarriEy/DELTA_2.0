from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Message as DBMessage, Conversation as DBConversation
from ..llm_integration import generate_response, generate_stream, generate_summary_from_messages
import logging

log = logging.getLogger(__name__)

def create_message(db: Session, content: str, sender: str, conversation_id: int, message_index: int):
    db_message = DBMessage(
        content=str(content),
        sender=sender,
        conversation_id=conversation_id,
        message_index=message_index,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

async def process_user_input(db: Session, user_input: str, conversation_id: int):
    conversation = db.query(DBConversation).filter(
        DBConversation.conversation_id == conversation_id
    ).first()

    if not conversation:
        return None, "Conversation not found"

    last_message_index = (
        db.query(func.max(DBMessage.message_index))
        .filter(DBMessage.conversation_id == conversation_id)
        .scalar()
    ) or 0

    # Create user message
    create_message(db, user_input, "user", conversation_id, last_message_index + 1)

    # Generate LLM response
    # (Simplified for now, excluding URL processing for brevity in this step)
    llm_response = await generate_response(user_input)

    # Create assistant message
    create_message(db, llm_response, "assistant", conversation_id, last_message_index + 2)

    return llm_response, None

async def process_user_input_stream(db: Session, user_input: str, conversation_id: int):
    conversation = db.query(DBConversation).filter(
        DBConversation.conversation_id == conversation_id
    ).first()

    if not conversation:
        yield "Error: Conversation not found"
        return

    last_message_index = (
        db.query(func.max(DBMessage.message_index))
        .filter(DBMessage.conversation_id == conversation_id)
        .scalar()
    ) or 0

    # Create user message
    create_message(db, user_input, "user", conversation_id, last_message_index + 1)

    full_response = ""
    async for chunk in generate_stream(user_input):
        full_response += chunk
        yield chunk

    # Create assistant message after stream ends
    create_message(db, full_response, "assistant", conversation_id, last_message_index + 2)

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

    return await generate_summary_from_messages(formatted_messages)
