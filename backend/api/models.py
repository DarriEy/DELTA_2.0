from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ARRAY, JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Database Configuration
raw_db_url = os.environ.get("DATABASE_URL")
if not raw_db_url:
    DATABASE_URL = "sqlite:///./fallback.db"
else:
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)

try:
    if "postgresql" in DATABASE_URL:
        engine = create_engine(DATABASE_URL, echo=True, connect_args={"connect_timeout": 10})
    else:
        engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Failed to create engine in models.py: {e}")
    # Define a dummy SessionLocal to prevent import errors
    SessionLocal = sessionmaker(bind=None)


Base = declarative_base()

# Define the Job model
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    parameters = Column(JSON)
    status = Column(String, default="PENDING", index=True)
    result = Column(JSON, nullable=True)
    logs = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

# Define the Conversation model
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Auto-incrementing
    conversation_id = Column(Integer, unique=True, index=True)  # Should this also be auto-incrementing?
    user_id = Column(Integer, index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    summary = Column(String, nullable=True)
    active_mode = Column(String, nullable=True)

    def __repr__(self):
        return f"<Conversation(id={self.id}, conversation_id={self.conversation_id}, user_id={self.user_id})>"

# Define the Message model
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, unique=True, index=True)
    conversation_id = Column(Integer, index=True)
    message_index = Column(Integer, index=True)
    sender = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Message(id={self.message_id}, conversation_id={self.conversation_id}, sender={self.sender})>"
    
# Define the Model Config model
class ModelConfig(Base):
    __tablename__ = "model_configs"

    config_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parameters = Column(JSON)  # Store parameters as a JSON object

    def __repr__(self):
        return f"<ModelConfig(name={self.name}, parameters={self.parameters})>"

# Define the Model Run model
class ModelRun(Base):
    __tablename__ = "model_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String)
    output_data = Column(String)

    def __repr__(self):
        return f"<ModelRun(run_id={self.run_id}, config_id={self.config_id}, status={self.status})>"

# Define the Educational Progress model
class EducationalProgress(Base):
    __tablename__ = "educational_progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    completed_topics = Column(ARRAY(String))
    quiz_scores = Column(JSON)  # Store quiz scores as a JSON object

    def __repr__(self):
        return f"<EducationalProgress(progress_id={self.progress_id}, user_id={self.user_id})>"

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()