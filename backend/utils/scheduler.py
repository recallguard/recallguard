"""APScheduler integration for RecallGuard."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from .refresh import refresh_recalls
from backend.api.ops import SCHEDULER_JOBS


_scheduler: BackgroundScheduler | None = None


def init_scheduler(app: Flask) -> BackgroundScheduler:
    """Initialize and start the APScheduler."""
    global _scheduler

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")

    def job() -> None:
        refresh_recalls()
        SCHEDULER_JOBS.inc()

    trigger = CronTrigger(hour=2, minute=30)
    _scheduler.add_job(job, trigger, id="refresh_recalls", replace_existing=True)
    _scheduler.start()

    @app.teardown_appcontext
    def shutdown(exception: Exception | None = None) -> None:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)

    return _scheduler
