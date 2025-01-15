# backend/models.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os
import logging

load_dotenv()
DATABASE_URL = f"postgresql+asyncpg://delta_user:{os.environ.get('DELTA_DB_PASSWORD')}@db/delta_db"

# Use declarative_base() to create the base class
Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=False)  # Set echo=True for debugging SQL

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    registration_date = Column(TIMESTAMP, server_default=func.now())

    conversations = relationship("Conversation", back_populates="user")
    model_configs = relationship("ModelConfig", back_populates="user")
    educational_progress = relationship(
        "EducationalProgress", back_populates="user"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    start_time = Column(TIMESTAMP, server_default=func.now())
    end_time = Column(TIMESTAMP)
    active_mode = Column(String)
    summary = Column(String, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"))
    message_index = Column(Integer)
    sender = Column(String)  # "user" or "assistant"
    content = Column(String)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class ModelConfig(Base):
    __tablename__ = "model_configs"

    config_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    config_name = Column(String)
    model_type = Column(String)  # Renamed from model_name
    config_data = Column(JSONB)
    creation_time = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="model_configs")
    model_runs = relationship("ModelRun", back_populates="config")


class ModelRun(Base):
    __tablename__ = "model_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("model_configs.config_id"))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    status = Column(String)
    output_path = Column(String)

    config = relationship("ModelConfig", back_populates="model_runs")


class EducationalProgress(Base):
    __tablename__ = "educational_progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    topic_name = Column(String)
    completion_status = Column(Boolean)
    last_accessed = Column(TIMESTAMP)
    quiz_score = Column(Integer)

    user = relationship("User", back_populates="educational_progress")

# Dependency to get the database session
async def get_db():
    async with async_session() as session:
        yield session

logging.basicConfig(level=logging.INFO)  # Configure logging
log = logging.getLogger(__name__)

async def create_tables():
    log.info(f"Creating tables using DATABASE_URL: {DATABASE_URL}") # Log the URL being used
    try:
        async with engine.begin() as conn:
            log.info("Engine connection established.")
            await conn.run_sync(Base.metadata.create_all)
            log.info("Tables created successfully.")
    except Exception as e:
        log.error(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())