from fastapi import APIRouter, HTTPException, Depends
from .llm_integration import generate_response, generate_image
from .schemas import UserInput, ImagePrompt
import yaml
import asyncpg
import subprocess
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate, User, ConversationCreate, Conversation, MessageCreate, Message, ModelConfigCreate, ModelConfig, ModelRunCreate, ModelRun, EducationalProgressCreate, EducationalProgress
from models import User as DBUser, Conversation as DBConversation, Message as DBMessage, ModelConfig as DBModelConfig, ModelRun as DBModelRun, EducationalProgress as DBEducationalProgress, get_db, engine
import bcrypt
from typing import List  # Import List from typing
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/api/process")
async def process_input(user_input: UserInput):
    try:
        llm_response = await generate_response(user_input.user_input)
        return {"llmResponse": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/learn")
async def learn_input(user_input: UserInput):
    try:
        llm_response = await generate_response(user_input.user_input, "EDUCATIONAL_GUIDE")
        return {"llmResponse": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate_image")
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


@router.post("/api/conversations/", response_model=Conversation)
async def create_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    print("Received conversation data:", conversation)
    try:
        # Correctly create the DBConversation object
        db_conversation = DBConversation(
            user_id=conversation.user_id,
            active_mode=conversation.active_mode
        )
        print("Creating DBConversation object:", db_conversation)

        # Add the new object to the session
        db.add(db_conversation)

        # Commit the transaction to save the object to the database
        await db.commit()

        # Refresh the object to get any generated values (like the ID)
        await db.refresh(db_conversation)

        # Return the newly created conversation
        return db_conversation
    except Exception as e:
        # If an error occurs, print it and raise an HTTPException
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
async def update_conversation(conversation_id: int, conversation_update: ConversationCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Fetch the existing conversation
        conversation = await db.get(DBConversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Update the conversation fields
        for key, value in conversation_update.dict(exclude_unset=True).items():
            setattr(conversation, key, value)

        # Commit the changes and refresh the object
        await db.commit()
        await db.refresh(conversation)
        return conversation