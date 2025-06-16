"""Logging configuration using loguru."""
import sys
from loguru import logger
from backend.config import settings


def configure_logging() -> None:
    logger.remove()
    if settings.env == "prod":
        logger.add(sys.stdout, serialize=True)
    else:
        logger.add(sys.stdout, colorize=True, format="<green>{time}</green> {level} {message}")


def get_logger() -> logger.__class__:
    return logger

