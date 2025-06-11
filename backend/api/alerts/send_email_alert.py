"""Send email digests for newly‑generated recall alerts
======================================================

This task retrieves the per‑user HTML bodies from
:pyfunc:`backend.api.alerts.generate_summary.build_user_digests`, delivers
them via SMTP (or an async provider such as Mailgun’s HTTP API), and then
marks the associated `Alert` rows as **sent**.

It is intended to run right after
``generate_summary.py`` – typically once or twice daily, but the interval
is configurable via the scheduler.
"""
from __future__ import annotations

import asyncio
import logging
import smtplib
from contextlib import asynccontextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable, Mapping

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Alert, User
from backend.db.session import get_async_session
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging
from .generate_summary import build_user_digests

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def _smtp_connection():
    """Async context‑manager that opens an SMTP connection and yields the object."""
    loop = asyncio.get_running_loop()

    def _connect() -> smtplib.SMTP:
        smtp = smtplib.SMTP(host=settings.smtp_host, port=settings.smtp_port, timeout=30)
        if settings.smtp_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        return smtp

    smtp: smtplib.SMTP = await loop.run_in_executor(None, _connect)
    try:
        yield smtp
    finally:
        await loop.run_in_executor(None, smtp.quit)


def _craft_message(to_addr: str, html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "⚠️ RecallGuard – Product Recall Digest"
    msg["From"] = settings.email_from
    msg["To"] = to_addr

    # Plain‑text fallback (rudimentary)
    msg.attach(MIMEText("Your email client does not support HTML."))
    msg.attach(MIMEText(html_body, "html"))
    return msg


async def _mark_alerts_sent(session: AsyncSession, alert_ids: Iterable[int]) -> None:
    if not alert_ids:
        return
    await session.execute(
        update(Alert)
        .where(Alert.id.in_(alert_ids))
        .values(sent_at="now()")
    )
    await session.commit()


async def send_alert_emails() -> None:
    """Main coroutine: send unsent recall digests and mark alerts as sent."""

    digests: Mapping[User, str]
    alert_map: Mapping[int, list[int]]  # user_id -> [alert_ids]

    async with get_async_session() as session:
        digests, alert_map = await build_user_digests(session)

    if not digests:
        logger.info("No new alerts to send – exiting early.")
        return

    async with _smtp_connection() as smtp:
        loop = asyncio.get_running_loop()
        for user, html_body in digests.items():
            msg = _craft_message(user.email, html_body)
            try:
                await loop.run_in_executor(None, smtp.send_message, msg)
                logger.info("Sent recall digest to %s", user.email)
            except Exception:
                logger.exception("Failed to send digest to %s", user.email)
                continue  # Do **not** mark as sent if email fails

            # Mark associated alerts as sent
            async with get_async_session() as session:
                await _mark_alerts_sent(session, alert_map[user.id])


def main() -> None:  # pragma: no cover
    """Entry‑point so the script can be executed directly."""
    setup_logging()
    asyncio.run(send_alert_emails())


if __name__ == "__main__":
    main()
