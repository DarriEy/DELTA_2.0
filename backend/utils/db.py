import logging
from typing import Optional, Callable, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from utils.settings import get_database_url

logger = logging.getLogger(__name__)

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def init_engine(echo: bool = False) -> Optional[Engine]:
    """Initialize the SQLAlchemy engine and session factory."""
    global _engine, _SessionLocal
    database_url = (get_database_url() or "").strip()
    redacted_url = "None"
    
    if not database_url:
        logger.warning("No database URL provided.")
        return None
    
    # Redact password for logging
    redacted_url = database_url
    
    logger.info("Initializing database engine with URL: %s", redacted_url)
    
    try:
        if "postgresql" in database_url:
            # Handle possible multiple @ in URL (sometimes in passwords)
            _engine = create_engine(
                database_url, echo=echo, connect_args={"connect_timeout": 10}
            )
        else:
            _engine = create_engine(database_url, echo=echo)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        return _engine
    except (Exception, ValueError) as exc:
        logger.error("Failed to create engine for %s. Error: %s", redacted_url, str(exc))
        
        # Specific check for common Neon/Render issues
        if "@" not in database_url or "://" not in database_url:
            logger.error("DATABASE_URL appears to be malformed or missing credentials.")
        
        # If the URL parsing failed, it might be due to special characters in password
        if "Could not parse SQLAlchemy URL" in str(exc) or "NoneType" in str(exc):
            logger.error("TIP: Ensure your database password does not contain special characters like '@', ':', or '/' without URL encoding.")
        
        _engine = None
        _SessionLocal = None
        return None


def get_engine() -> Optional[Engine]:
    if _engine is None:
        init_engine(echo=False)
    return _engine


def get_session_local() -> Optional[sessionmaker]:
    if _SessionLocal is None:
        init_engine(echo=False)
    return _SessionLocal


def get_db() -> Generator[Optional[Session], None, None]:
    session_factory = get_session_local()
    if not session_factory:
        logger.warning("Database session factory not available. Yielding None for DB session.")
        yield None
        return
        
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
