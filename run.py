"""
Recall Guard – project launcher
================================

Usage examples
--------------
# Start API server (default)
$ python run.py
# or explicitly
$ python run.py api

# Start background worker (Celery)
$ python run.py worker

# Start periodic-task scheduler (Celery beat)
$ python run.py beat
"""

from __future__ import annotations

import os
import sys
from typing import Callable

# Local utilities (to be implemented next)
from backend.utils.config import settings          # Typed Pydantic settings object
from backend.utils.logging import configure_logging

# --------------------------------------------------------------------------- #
# Boot helpers
# --------------------------------------------------------------------------- #

def start_api() -> None:
    """Run the FastAPI application with Uvicorn."""
    import uvicorn
    from backend.api.main import create_app       # factory we’ll write in backend/api/main.py

    configure_logging(settings.LOG_LEVEL)
    app = create_app()                            # returns FastAPI instance
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,                   # auto-reload only in dev
        log_level=settings.UVICORN_LOG_LEVEL,
    )


def start_worker() -> None:
    """Run Celery worker for background jobs (e.g., recall fetch, email alerts)."""
    from backend.utils.scheduler import make_celery   # wraps Celery config

    celery_app = make_celery()
    # Equivalent to: celery -A backend.utils.scheduler worker --loglevel=info
    celery_app.worker_main(["worker", "--loglevel=INFO"])


def start_beat() -> None:
    """Run Celery beat scheduler for periodic tasks."""
    from backend.utils.scheduler import make_celery

    celery_app = make_celery()
    celery_app.start(argv=["celery", "beat", "--loglevel=INFO"])


# Map CLI arg ➜ function
COMMANDS: dict[str, Callable[[], None]] = {
    "api": start_api,
    "worker": start_worker,
    "beat": start_beat,
}


# --------------------------------------------------------------------------- #
# Main dispatcher
# --------------------------------------------------------------------------- #

def main() -> None:
    """Parse CLI arg and dispatch to the appropriate starter."""
    cmd = sys.argv[1] if len(sys.argv) > 1 else "api"
    runner = COMMANDS.get(cmd)
    if runner is None:
        valid = ", ".join(COMMANDS.keys())
        sys.exit(f"[run.py] Unknown command '{cmd}'. Valid options: {valid}")
    runner()


if __name__ == "__main__":
    main()
