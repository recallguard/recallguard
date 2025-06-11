# backend/utils/logging.py

from __future__ import annotations
import logging
import logging.config
import sys
from typing import Any, Dict

from .config import get_settings


def _default_dict_config(level: str) -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
            }
        },
        "root": {"level": level, "handlers": ["console"]},
    }


def setup_logging(*, override_level: str | None = None) -> None:
    settings = get_settings()
    level = (override_level or settings.log_level).upper()

    if settings.logging_config:
        cfg: Dict[str, Any] = settings.logging_config  # type: ignore[assignment]
    else:
        cfg = _default_dict_config(level)

    logging.config.dictConfig(cfg)

    if level != "DEBUG":
        for noisy in ("httpx", "urllib3", "botocore"):
            logging.getLogger(noisy).setLevel("WARNING")

    logging.getLogger(__name__).info("Logging initialized at %s level", level)


def get_logger(name: str) -> logging.Logger:
    """Shorthand for retrieving a configured logger."""
    return logging.getLogger(name)
