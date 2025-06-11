"""Centralized APScheduler helper for RecallGuard
================================================

This module exposes a *singleton* AsyncIO‑based scheduler configured with a
PostgreSQL (or SQLite) job‑store so that jobs persist across restarts.  All
periodic tasks (e.g. fetching recall feeds, summarising alerts, emailing
users) should be registered **once** at application start‑up via
:pyfunc:`get_scheduler`.

Example (FastAPI)
-----------------
>>> from fastapi import FastAPI
>>> from utils.scheduler import get_scheduler, register_default_jobs
>>> app = FastAPI()
>>> scheduler = get_scheduler(app)
>>> register_default_jobs()
>>> scheduler.start()
"""
from __future__ import annotations

import asyncio
from datetime import timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Coroutine

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import get_settings

__all__ = [
    "get_scheduler",
    "register_default_jobs",
    "add_job_once",
]


# ---------------------------------------------------------------------------
# Singleton scheduler factory
# ---------------------------------------------------------------------------

_scheduler: AsyncIOScheduler | None = None


def get_scheduler(app: Any | None = None) -> AsyncIOScheduler:  # noqa: ANN401
    """Return the (lazy‑initialised) AsyncIO scheduler instance.

    The scheduler uses a SQLAlchemy job‑store so that jobs are durable across
    process restarts (handy for containers / server restarts).  The DB URI is
    pulled from :pyfunc:`utils.config.get_settings`.
    """
    global _scheduler  # noqa: PLW0603

    if _scheduler is not None:
        return _scheduler

    settings = get_settings()

    jobstores = {
        "default": SQLAlchemyJobStore(url=settings.scheduler_db_uri or settings.database_uri),
    }

    executors = {
        "default": ThreadPoolExecutor(max_workers=10),
    }

    job_defaults = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 60 * 5,  # 5 minutes
    }

    _scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.timezone or timezone.utc,
    )

    # Optionally attach to FastAPI / Starlette lifespan so jobs stop cleanly
    if app is not None and hasattr(app, "add_event_handler"):
        app.add_event_handler("startup", _scheduler.start)
        app.add_event_handler("shutdown", _scheduler.shutdown)

    return _scheduler


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def _import_string(dotted_path: str) -> Callable[[], Coroutine[Any, Any, Any]] | Callable[..., Any]:
    """Import a callable from dotted path string (lazy import to reduce overhead)."""
    module_path, attr = dotted_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, attr)


def add_job_once(
    func: str | Callable[..., Any],
    trigger: CronTrigger | dict[str, Any],
    *,
    job_id: str,
    replace_existing: bool = True,
    **kwargs: Any,
) -> None:
    """Add a job if it doesn't already exist (idempotent)."""
    scheduler = get_scheduler()

    try:
        scheduler.get_job(job_id)
    except JobLookupError:
        callable_: Any
        if isinstance(func, str):
            callable_ = _import_string(func)
        else:
            callable_ = func

        if isinstance(trigger, dict):
            trigger = CronTrigger(**trigger)

        scheduler.add_job(
            callable_,
            trigger=trigger,  # type: ignore[arg-type]
            id=job_id,
            replace_existing=replace_existing,
            kwargs=kwargs,
        )


# ---------------------------------------------------------------------------
# Default project jobs
# ---------------------------------------------------------------------------

_DEFAULT_CRONS = {
    # Fetch recall feeds hourly
    "recall_cpsc": {"minute": 0, "second": 0},
    "recall_fda": {"minute": 10, "second": 0},
    "recall_nhtsa": {"minute": 20, "second": 0},
    "recall_usda": {"minute": 30, "second": 0},

    # Summarise and send alerts every morning at 09:00 local time
    "daily_summary": {"hour": 9, "minute": 0},
}

_DEFAULT_TASKS = {
    "recall_cpsc": "backend.api.recalls.fetch_cpsc.run",  # function must be async/awaitable or regular callable
    "recall_fda": "backend.api.recalls.fetch_fda.run",
    "recall_nhtsa": "backend.api.recalls.fetch_nhtsa.run",
    "recall_usda": "backend.api.recalls.fetch_usda.run",
    "daily_summary": "backend.api.alerts.generate_summary.run",
}


def register_default_jobs() -> None:
    """Register built‑in periodic background tasks.

    Call this once during application start‑up *after* importing all service
    modules to avoid cyclic imports.
    """
    for job_id, cron in _DEFAULT_CRONS.items():
        add_job_once(_DEFAULT_TASKS[job_id], cron, job_id=job_id)


# ---------------------------------------------------------------------------
# CLI helper (for debugging)
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import uvloop

    uvloop.install()

    async def _main() -> None:
        scheduler = get_scheduler()
        register_default_jobs()
        scheduler.start()
        print("Scheduler started. Jobs:")
        for job in scheduler.get_jobs():
            print("  ", job)
        # Keep the loop alive forever (Ctrl‑C to exit)
        await asyncio.Event().wait()

    asyncio.run(_main())
