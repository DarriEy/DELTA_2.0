from fastapi import APIRouter, HTTPException, Depends, Body
from .schemas import UserInput, ImagePrompt, ConversationCreate
import yaml
import json
import asyncpg
import subprocess
from sqlalchemy.future import select
from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserCreate, User, ConversationCreate, Conversation, MessageCreate, Message, ModelConfigCreate, ModelConfig, ModelRunCreate, ModelRun, EducationalProgressCreate, EducationalProgress, ConversationUpdate
from .models import User as DBUser, Conversation as DBConversation, Message as DBMessage, ModelConfig as DBModelConfig, ModelRun as DBModelRun, EducationalProgress as DBEducationalProgress, get_db, engine, SessionLocal
from .llm_integration import (
    generate_response,
    generate_image,
    generate_summary_from_messages,
)
import bcrypt
from typing import List  # Import List from typing
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

import logging

log = logging.getLogger(__name__)

router = APIRouter()

async def create_message_in_db(db, content, sender, conversation_id, message_index):
    """Helper function to create a message in the database."""
    db_message = DBMessage(
        content=content,
        sender=sender,
        conversation_id=conversation_id,
        message_index=message_index
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

@router.post("/api/process")
async def process_input(user_input: str = Body(...), conversation_id: int = Body(...), db: AsyncSession = Depends(get_db)):
    log.info(f"Processing input: {user_input} for conversation: {conversation_id}")
    try:
        # Get the conversation from the database
        
        result = await db.execute(select(DBConversation).where(DBConversation.conversation_id == conversation_id))
        conversation = result.scalars().first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Fetch the last message index for this conversation
        result = await db.execute(
            select(func.max(DBMessage.message_index)).where(DBMessage.conversation_id == conversation_id)
        )
        last_message_index = result.scalar() or 0

        # Create a new message entry in the database for the user input
        await create_message_in_db(db, user_input, "user", conversation_id, last_message_index + 1)

        # Generate LLM response
        llm_response = await generate_response(user_input)

        # Create a new message entry in the database for the LLM response
        await create_message_in_db(db, llm_response, "assistant", conversation_id, last_message_index + 2)

        return {"llmResponse": llm_response}
    except Exception as e:
        log.error(f"Error in process_input: {e}") # Log any errors
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/api/learn")
async def learn_input(user_input: str = Body(...), conversation_id: int = Body(...), db: AsyncSession = Depends(get_db)):
    try:
        # Get the conversation from the database
        result = await db.execute(select(DBConversation).where(DBConversation.conversation_id == conversation_id))
        conversation = result.scalars().first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Fetch the last message index for this conversation
        result = await db.execute(
            select(func.max(DBMessage.message_index)).where(DBMessage.conversation_id == conversation_id)
        )
        last_message_index = result.scalar() or 0

        # Create a new message entry in the database for the user input
        await create_message_in_db(db, user_input, "user", conversation_id, last_message_index + 1)

        # Generate LLM response
        llm_response = await generate_response(user_input, "EDUCATIONAL_GUIDE")

        # Create a new message entry in the database for the LLM response
        await create_message_in_db(db, llm_response, "assistant", conversation_id, last_message_index + 2)

        return {"llmResponse": llm_response}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate_image/")
async def generate_image_route(prompt_data: ImagePrompt):
    try:
        data_uri = await generate_image(prompt_data.prompt)
        if data_uri:
            return {"image_url": data_uri}
        else:
            raise HTTPException(status_code=500, detail="Image generation failed")
    except Exception as e:
        print(f"Error in generate_image_route: {e}")
        # Customize error messages based on the exception type
        if isinstance(e, HTTPException):
            raise e  # Re-raise HTTPException instances to retain their status codes
        elif "specific error condition" in str(e):
            raise HTTPException(status_code=400, detail="Invalid prompt: specific error condition")
        else:
            raise HTTPException(status_code=500, detail="Image generation failed due to an unexpected error")
        

@router.post("/api/run_confluence")
async def run_confluence(input_data: dict):
    try:
        model = input_data.get("model")
        config_path = input_data.get("configPath")

        # Load and update the configuration file
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        config['HYDROLOGICAL_MODEL'] = model

        # Save the updated configuration file
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f)

        # Run CONFLUENCE using subprocess
        confluence_path = "/Users/darrieythorsson/compHydro/code/CONFLUENCE/CONFLUENCE.py"  # Replace with the actual path to confluence.py
        process = subprocess.run(
            ["python", confluence_path, "--config", config_path],
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=process.stderr)

        return {"message": "CONFLUENCE run started", "output": process.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/api/users/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Check if a user with the given email already exists
        result = await db.execute(select(DBUser).where(DBUser.email == user.email))
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(status_code=409, detail="Email already exists")

        # If the user doesn't exist, proceed with creation
        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        db_user = DBUser(
            username=user.username, email=user.email, password_hash=hashed_password
        )
        db.add(db_user)
        try:
            await db.commit()
            await db.refresh(db_user)  # Inside async with and try block
            return db_user
        except Exception as e:  # Catch general exception
            await db.rollback()
            print(f"Error creating user: {e}")  # Log the error
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}") # Raise inside async with block


# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/api/conversations/", response_model=Conversation)
async def create_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    print("Received conversation data:", conversation)
    print("Conversation as dict:", conversation.dict())
    try:
        async with db.begin():
            db_conversation = DBConversation(**conversation.dict())
            db_conversation.user_id = 1  # Set a user_id temporarily
            print("Creating DBConversation object:", db_conversation)
            db.add(db_conversation)
            await db.flush()
            await db.refresh(db_conversation)
            print("Conversation object after refresh:", db_conversation)
            await db.commit()
            return db_conversation
    except Exception as e:
        await db.rollback()
        print(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.get("/api/conversations/{user_id}", response_model=List[Conversation])
async def get_conversations(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(DBConversation).where(DBConversation.user_id == user_id))
        conversations = result.scalars().all()
        return conversations

@router.post("/api/messages/", response_model=Message)
async def create_message(message: MessageCreate, conversation_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        db_message = DBMessage(**message.dict(), conversation_id=conversation_id)
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

@router.get("/api/messages/{conversation_id}", response_model=List[Message])
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(DBMessage).where(DBMessage.conversation_id == conversation_id).order_by(DBMessage.message_index))
        messages = result.scalars().all()
        return messages

@router.put("/api/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: int, conversation_update: ConversationUpdate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Fetch the existing conversation
        conversation = await db.get(DBConversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Update the conversation fields
        update_data = conversation_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)

        # Refresh and then commit the changes
        await db.refresh(conversation)  # Refresh happens *before* commit
        await db.commit()
        return conversation
    
@router.get("/api/summary/{conversation_id}")
async def get_summary(conversation_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Fetch conversation messages
        result = await db.execute(
            select(DBMessage)
            .where(DBMessage.conversation_id == conversation_id)
            .order_by(DBMessage.message_index)
        )
        messages = result.scalars().all()

        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Format messages for LLM prompt
        formatted_messages = [
            {"role": msg.sender, "content": msg.content} for msg in messages
        ]

        # Generate summary using LLM
        try:
            summary = await generate_response(
                f"Summarize the following conversation: {json.dumps(formatted_messages)}"
            )
            return {"summary": summary}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating summary: {e}",
            )
        
@router.get("/api/summary/{conversation_id}")
async def get_summary(conversation_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Fetch conversation messages
        result = await db.execute(
            select(DBMessage)
            .where(DBMessage.conversation_id == conversation_id)
            .order_by(DBMessage.message_index)
        )
        messages = result.scalars().all()

        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Format messages for LLM prompt
        formatted_messages = [
            {"role": msg.sender, "content": msg.content} for msg in messages
        ]

        # Generate summary using LLM
        try:
            summary = await generate_response(
                f"Summarize the following conversation: {json.dumps(formatted_messages)}"
            )
            return {"summary": summary}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating summary: {e}",
            )
        
@router.get("/api/summary/{conversation_id}")
async def get_summary(conversation_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Fetch conversation messages
        result = await db.execute(
            select(DBMessage)
            .where(DBMessage.conversation_id == conversation_id)
            .order_by(DBMessage.message_index)
        )
        messages = result.scalars().all()

        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Convert messages to a simpler format
        formatted_messages = [
            {"sender": msg.sender, "content": msg.content} for msg in messages
        ]

        # Generate summary using the dedicated function
        try:
            summary = await generate_summary_from_messages(formatted_messages)
            return {"summary": summary}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating summary: {e}",
            )
        
@router.get("/api/health")
async def health_check():
    return {"status": "ok"}