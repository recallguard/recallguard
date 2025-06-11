"""backend/api/products/email_import.py

Import purchased items from a user’s email receipts.

Many users prefer a *zero-touch* onboarding: they link their email address
and RecallGuard automatically extracts UPCs/model numbers from purchase
receipts (Amazon, Walmart, etc.) and creates `Product` entries.

This module provides:

* IMAPConnector – IMAP/XOAUTH2 polling.
* AbstractReceiptParser – store-specific parsing.
* run_email_import – APScheduler job entrypoint.
"""
from __future__ import annotations

import email
import imaplib
import re
import ssl
from contextlib import contextmanager
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Iterable, List, Protocol, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session

from backend.db.models import Product, User
from backend.utils.config import get_settings
from backend.utils.logging import get_logger
from backend.utils.db import get_engine

# Expose API
__all__ = ["run_email_import", "AbstractReceiptParser"]

logger = get_logger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# IMAP helper
# ---------------------------------------------------------------------------

@contextmanager
def _imap_connection(server: str, port: int, email_addr: str, oauth2_token: str):
    """Context-managed IMAP SSL connection using XOAUTH2."""
    logger.debug("Connecting to IMAP server %s:%s as %s", server, port, email_addr)
    ctx = ssl.create_default_context()
    with imaplib.IMAP4_SSL(server, port, ssl_context=ctx) as imap:
        auth_str = f"user={email_addr}\1auth=Bearer {oauth2_token}\1\1"
        typ, _ = imap.authenticate("XOAUTH2", lambda _: auth_str)
        if typ != "OK":
            raise RuntimeError(f"IMAP auth failed for {email_addr}")
        yield imap

# ---------------------------------------------------------------------------
# Receipt parsing framework
# ---------------------------------------------------------------------------

ProductDTO = Tuple[str, str, datetime, str]  # UPC, name, date, image_url

class AbstractReceiptParser(Protocol):
    """Pluggable parser for a single merchant."""

    store: str

    def supports(self, msg: EmailMessage) -> bool:
        ...

    def parse(self, msg: EmailMessage) -> List[ProductDTO]:
        ...

class AmazonParser:
    store = "amazon"
    _order_re = re.compile(r"Your Amazon\.com order of (.*)")
    _upc_re   = re.compile(r"UPC\s*:\s*(\d{12,14})")

    def supports(self, msg: EmailMessage) -> bool:
        return "amazon.com" in msg.get("From", "").lower() and "order" in msg.get("Subject", "").lower()

    def parse(self, msg: EmailMessage) -> List[ProductDTO]:
        body = msg.get_body(preferencelist=("plain","html")).get_content()
        upcs = self._upc_re.findall(body)
        name_m = self._order_re.search(msg.get("Subject",""))
        name = name_m.group(1) if name_m else "Amazon Purchase"
        dt = datetime.now(timezone.utc)
        return [(upc, name, dt, "") for upc in upcs]

PARSERS: list[AbstractReceiptParser] = [AmazonParser()]

# ---------------------------------------------------------------------------
# Core workflow
# ---------------------------------------------------------------------------

def _fetch_unseen(imap: imaplib.IMAP4_SSL, since_uid: int|None) -> Iterable[bytes]:
    imap.select("INBOX")
    crit = "(UNSEEN)" if since_uid is None else f"(UID {since_uid+1}:*)"
    typ, data = imap.uid("SEARCH", None, crit)
    if typ != "OK":
        logger.error("IMAP search failed: %s", data)
        return ()
    for uid in data[0].split():
        typ, msgdata = imap.uid("FETCH", uid, "(RFC822)")
        if typ == "OK":
            yield msgdata[0][1]

def _upsert(session: Session, user: User, items: List[ProductDTO]):
    for upc, name, dt, img in items:
        try:
            p = Product(
                user_id=user.id,
                upc=upc,
                name=name,
                purchase_date=dt,
                image_url=img,
                source="email",
            )
            session.add(p)
            session.flush()
        except IntegrityError:
            session.rollback()
            logger.debug("Duplicate %s for user %s, skipping", upc, user.email)

def run_email_import():
    """APScheduler job: poll IMAP for enabled users and import receipts."""
    engine = get_engine(settings.DATABASE_URI)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        users = session.scalars(
            select(User).where(User.email_import_enabled.is_(True))
        ).all()

        logger.info("Email import for %d user(s)", len(users))
        for user in users:
            if not user.imap_server or not user.oauth_token:
                logger.warning("Skipping %s: no IMAP creds", user.email)
                continue

            try:
                with _imap_connection(
                    user.imap_server, user.imap_port or 993,
                    user.email, user.oauth_token
                ) as imap:
                    raw_msgs = _fetch_unseen(imap, user.last_email_uid)
                    for raw in raw_msgs:
                        msg = email.message_from_bytes(raw)
                        for parser in PARSERS:
                            if parser.supports(msg):
                                products = parser.parse(msg)
                                if products:
                                    _upsert(session, user, products)
                                break

                    # bump last UID checkpoint
                    typ, all_uids = imap.uid("SEARCH", None, "UID *")
                    if typ == "OK" and all_uids[0]:
                        user.last_email_uid = int(all_uids[0].split()[-1])
                    session.commit()

            except Exception as e:
                logger.exception("Email import failed for %s", user.email)

if __name__ == "__main__":
    run_email_import()
