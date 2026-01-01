import logging

from backend.utils.logging_config import setup_logging, get_logger


def test_setup_logging_configures_logger():
    setup_logging("WARNING")
    logger = get_logger("delta.test")

    assert isinstance(logger, logging.Logger)
    assert logging.getLogger().level == logging.WARNING
