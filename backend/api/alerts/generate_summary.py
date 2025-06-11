"""Generate per‑user digest text for recall alerts
=================================================

This task collates all *un‑sent* `Alert` rows, groups them by user, and
renders an email‑ready markdown (or HTML) body summarising which of their
products were recalled, the severity, and link‑outs to the official recall
notices.

How it works
------------
1. Fetch all `Alert` rows where `sent_at IS NULL`.
2. Group by `user_id` and gather the full `Recall` entity for context.
3. Render a summary using **Jinja2** templates (stored under
   `backend/templates/email/recall_digest.html`).
4. Persist the rendered HTML in the `email_body` column (added via
   migration) and mark the `Alert` rows as `summarised_at` so the
   downstream email sender can pick them up.

If `USE_AI_SUMMARY` is enabled in config, we send a quick summary prompt
to OpenAI to generate a short, empathetic intro paragraph that precedes
the bullet‑list of affected items.
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ...db.session import get_session  # lazily initialised engine/session
from ...db import models as m
from ...utils.config import get_settings
from ...utils.ai_helpers import chat_complete  # thin wrapper around OpenAI
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent.parent / "templates" / "email"),
    autoescape=select_autoescape(["html", "xml"]),
)
_digest_tmpl = _env.get_template("recall_digest.html")


def _ai_intro(recall_count: int) -> str:
    """Generate a human‑sounding intro line via LLM."""

    if not settings.use_ai_summary:
        return (
            "Below is a summary of new product recalls that might affect items you own. "
            "Please review the details and take action where necessary."
        )

    prompt = (
        "You are RecallGuard, a helpful assistant. Craft one friendly paragraph (max 60 words) "
        f"introducing a recall email that contains {recall_count} items. Keep it plain‑spoken, "
        "empathetic, and action‑oriented."
    )

    resp = chat_complete(prompt, temperature=0.7, max_tokens=80)
    return resp.strip()


def _render_body(user: m.User, recalls: List[m.Recall]) -> str:
    intro = _ai_intro(len(recalls))
    return _digest_tmpl.render(user=user, intro=intro, recalls=recalls, settings=settings)


def generate_summaries(session: Session | None = None) -> int:
    """Main entrypoint – returns the number of users processed."""

    owns_session = session is None
    if owns_session:
        session = get_session()

    try:
        pending: Iterable[m.Alert] = session.scalars(
            select(m.Alert).where(m.Alert.sent_at.is_(None))
        ).all()
        if not pending:
            logger.info("No pending alerts found – nothing to summarise.")
            return 0

        per_user: dict[int, list[m.Alert]] = defaultdict(list)
        for alert in pending:
            per_user[alert.user_id].append(alert)

        for user_id, alerts in per_user.items():
            user = session.get(m.User, user_id)
            recalls = [alert.recall for alert in alerts]
            html_body = _render_body(user, recalls)

            # Store the rendered body in *one* alert row (first) to avoid duplication.
            alerts[0].email_body = html_body
            alerts[0].summarised_at = dt.datetime.utcnow()

            # Mark the rest as summarised (without email_body)
            for a in alerts[1:]:
                a.summarised_at = alerts[0].summarised_at

        session.commit()
        logger.info("Generated summaries for %d users", len(per_user))
        return len(per_user)

    except Exception:
        session.rollback()
        logger.exception("Failed generating summaries – transaction rolled back.")
        raise

    finally:
        if owns_session:
            session.close()


if __name__ == "__main__":
    generate_summaries()
