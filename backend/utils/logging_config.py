import logging
from typing import Optional

from utils.settings import get_env, load_environment


def setup_logging(level: Optional[str] = None) -> None:
    load_environment()
    log_level = (level or get_env("LOG_LEVEL", "INFO")).upper()
    if not logging.getLogger().handlers:
        logging.basicConfig(level=log_level)
    logging.getLogger().setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
