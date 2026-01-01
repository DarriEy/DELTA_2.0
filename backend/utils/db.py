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
    database_url = get_database_url()
    
    # Redact password for logging
    redacted_url = database_url
    if "@" in database_url and "://" in database_url:
        prefix, rest = database_url.split("://", 1)
        if "@" in rest:
            auth, host = rest.split("@", 1)
            redacted_url = f"{prefix}://***:***@{host}"
    
    logger.info("Initializing database engine with URL: %s", redacted_url)
    
    try:
        if "postgresql" in database_url:
            _engine = create_engine(
                database_url, echo=echo, connect_args={"connect_timeout": 10}
            )
        else:
            _engine = create_engine(database_url, echo=echo)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        return _engine
    except Exception as exc:
        logger.error("Failed to create engine for %s: %s", redacted_url, exc)
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


def get_db() -> Generator[Session, None, None]:
    session_factory = get_session_local()
    if not session_factory:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database connection unavailable")
        
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
