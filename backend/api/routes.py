from fastapi import APIRouter, HTTPException, Depends, status, Body
from .schemas import UserInput, ImagePrompt, ConversationCreate
import yaml
import json
import asyncpg
import subprocess
from sqlalchemy.future import select
from sqlalchemy import update, func
from .schemas import (
    UserCreate,
    User,
    ConversationCreate,
    Conversation,
    MessageCreate,
    Message,
    ModelConfigCreate,
    ModelConfig,
    ModelRunCreate,
    ModelRun,
    EducationalProgressCreate,
    EducationalProgress,
    ConversationUpdate,
)
from .models import (
    User as DBUser,
    Conversation as DBConversation,
    Message as DBMessage,
    ModelConfig as DBModelConfig,
    ModelRun as DBModelRun,
    EducationalProgress as DBEducationalProgress,
    get_db,
)
from .llm_integration import (
    generate_response,
    generate_image,
    generate_summary_from_messages,
)
import bcrypt
from typing import List  # Import List from typing
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

import logging

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

router = APIRouter()


def create_message_in_db(db, content, sender, conversation_id, message_index):
    """Helper function to create a message in the database."""
    db_message = DBMessage(
        content=content,
        sender=sender,
        conversation_id=conversation_id,
        message_index=message_index,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.post("/process")
def process_input(
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    log.info(f"Processing input: {user_input} for conversation: {conversation_id}")
    try:
        # Get the conversation from the database

        conversation = db.query(DBConversation).filter(
            DBConversation.conversation_id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Fetch the last message index for this conversation
        last_message_index = (
            db.query(func.max(DBMessage.message_index))
            .filter(DBMessage.conversation_id == conversation_id)
            .scalar()
        ) or 0

        # Create a new message entry in the database for the user input
        create_message_in_db(
            db, user_input, "user", conversation_id, last_message_index + 1
        )

        # Generate LLM response
        llm_response = generate_response(user_input)

        # Create a new message entry in the database for the LLM response
        create_message_in_db(
            db, llm_response, "assistant", conversation_id, last_message_index + 2
        )

        return {"llmResponse": llm_response}
    except Exception as e:
        log.error(f"Error in process_input: {e}")  # Log any errors
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
def learn_input(
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    try:
        # Get the conversation from the database
        conversation = db.query(DBConversation).filter(
            DBConversation.conversation_id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Fetch the last message index for this conversation
        last_message_index = (
            db.query(func.max(DBMessage.message_index))
            .filter(DBMessage.conversation_id == conversation_id)
            .scalar()
        ) or 0

        # Create a new message entry in the database for the user input
        create_message_in_db(
            db, user_input, "user", conversation_id, last_message_index + 1
        )

        # Generate LLM response
        llm_response = generate_response(user_input, "EDUCATIONAL_GUIDE")

        # Create a new message entry in the database for the LLM response
        create_message_in_db(
            db, llm_response, "assistant", conversation_id, last_message_index + 2
        )

        return {"llmResponse": llm_response}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_image/")
async def generate_image_route(prompt_data: ImagePrompt):  # Marked as async
    print(f"generate_image_route called with prompt: {prompt_data.prompt}")
    try:
        data_uri = await generate_image(prompt_data.prompt)  # Await the coroutine
        if data_uri:
            return {"image_url": data_uri}
        else:
            raise HTTPException(status_code=500, detail="Image generation failed")
    except Exception as e:
        print(f"Error in generate_image_route: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Image generation failed")


@router.post("/run_confluence")
async def run_confluence(input_data: dict):
    try:
        model = input_data.get("model")
        config_path = input_data.get("configPath")

        # Load and update the configuration file
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        config["HYDROLOGICAL_MODEL"] = model

        # Save the updated configuration file
        with open(config_path, "w") as f:
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


@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if a user with the given email already exists
    existing_user = db.query(DBUser).filter(DBUser.email == user.email).first()

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
        db.commit()
        db.refresh(db_user)  # Inside async with and try block
        return db_user
    except Exception as e:  # Catch general exception
        db.rollback()
        print(f"Error creating user: {e}")  # Log the error
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        )  # Raise inside async with block


@router.post("/conversations/", response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate, db: Session = Depends(get_db)
):
    print("Received conversation data:", conversation)
    print("Conversation as dict:", conversation.dict())
    try:
        db_conversation = DBConversation(**conversation.dict())
        print("Creating DBConversation object:", db_conversation)
        db.add(db_conversation)
        db.flush()
        db.refresh(db_conversation)
        print("Conversation object after refresh:", db_conversation)

        # Convert the ORM object to a dictionary that Pydantic can validate against the response_model
        conversation_dict = {
            "conversation_id": db_conversation.id,
            "user_id": db_conversation.user_id,
            "start_time": db_conversation.start_time,
            "end_time": db_conversation.end_time,
            "summary": db_conversation.summary,
            "active_mode": db_conversation.active_mode
        }

        return conversation_dict
    except Exception as e:
        db.rollback()
        print(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.get("/conversations/{user_id}", response_model=List[Conversation])
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(DBConversation).filter(DBConversation.user_id == user_id).all()
    return conversations


@router.post("/messages/", response_model=Message)
def create_message(
    message: MessageCreate, conversation_id: int, db: Session = Depends(get_db)
):
    db_message = DBMessage(**message.dict(), conversation_id=conversation_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/messages/{conversation_id}", response_model=List[Message])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index)
        .all()
    )
    return messages


@router.put("/conversations/{conversation_id}", response_model=Conversation)
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
):
    # Fetch the existing conversation
    conversation = db.query(DBConversation).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update the conversation fields
    update_data = conversation_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)

    db.refresh(conversation)
    db.commit()
    return conversation


@router.get("/summary/{conversation_id}")
async def get_summary(conversation_id: int, db: Session = Depends(get_db)):
    # Fetch conversation messages
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.message_index)
        .all()
    )

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


def get_webpage_content(url: str) -> str:
    """Fetches and extracts the main content of a webpage."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from specific tags or classes if needed
        # For example, if the main content is within <article> tags:
        # main_content = soup.find('article').get_text()
        main_content = soup.get_text()  # Extracts all text

        return main_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage content: {e}")
        return ""

@router.post("/process")
def process_input(
    user_input: str = Body(...),
    conversation_id: int = Body(...),
    db: Session = Depends(get_db),
):
    log.info(f"Processing input: {user_input} for conversation: {conversation_id}")
    try:
        # Get the conversation from the database
        conversation = db.query(DBConversation).filter(
            DBConversation.conversation_id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Fetch the last message index for this conversation
        last_message_index = (
            db.query(func.max(DBMessage.message_index))
            .filter(DBMessage.conversation_id == conversation_id)
            .scalar()
        ) or 0

        # Create a new message entry in the database for the user input
        create_message_in_db(
            db, user_input, "user", conversation_id, last_message_index + 1
        )

        # Check if the user_input is a URL
        if user_input.startswith("http://") or user_input.startswith("https://"):
            content = get_webpage_content(user_input)
            if content:
                # Generate a response based on the content of the URL
                llm_response = generate_response(f"Here is content from a webpage: {content}")
            else:
                llm_response = "Could not fetch content from the provided URL."
        else:
            # Generate LLM response for normal text input
            llm_response = generate_response(user_input)

        # Create a new message entry in the database for the LLM response
        create_message_in_db(
            db, llm_response, "assistant", conversation_id, last_message_index + 2
        )

        return {"llmResponse": llm_response}

    except Exception as e:
        log.error(f"Error in process_input: {e}")  # Log any errors
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))