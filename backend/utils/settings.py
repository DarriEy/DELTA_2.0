import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback for minimal test envs
    def load_dotenv(*_args, **_kwargs):
        return False

_ENV_LOADED = False


def load_environment() -> None:
    """Load environment variables once from .env and ~/.env_delta."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    load_dotenv()
    home_env_path = os.path.expanduser("~/.env_delta")
    if os.path.exists(home_env_path):
        load_dotenv(home_env_path)
    _ENV_LOADED = True


def reset_environment_for_tests() -> None:
    """Reset env loading state for test isolation."""
    global _ENV_LOADED
    _ENV_LOADED = False


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    load_environment()
    return os.environ.get(key, default)


def get_database_url() -> str:
    raw_db_url = get_env("DATABASE_URL")
    if not raw_db_url:
        logger.warning("DATABASE_URL not set, falling back to SQLite")
        return "sqlite:///./fallback.db"
    
    raw_db_url = raw_db_url.strip()
    
    # Render and other providers often use postgres://, but SQLAlchemy requires postgresql://
    if raw_db_url.startswith("postgres://"):
        return raw_db_url.replace("postgres://", "postgresql://", 1)
    return raw_db_url
