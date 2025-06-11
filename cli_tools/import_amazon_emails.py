"""
cli_tools/import_amazon_emails.py
=================================
Admin-side helper that logs into a Gmail (or any IMAP) inbox, searches for
Amazon order-confirmation emails, parses ASIN / UPC values from the receipts,
and inserts matching `Product` rows into RecallGuard for a specified user.

Typical usage
-------------

# Import products for jane@example.com, scanning mail since 2025-01-01
python -m cli_tools.import_amazon_emails \
    --email jane@example.com \
    --imap-user yourbot@gmail.com \
    --imap-pass app-password-here \
    --since 2025-01-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import email
import imaplib
import logging
import os
import re
import sys
from email.header import decode_header, make_header
from pathlib import Path
from typing import Iterable, List

import bs4
from sqlalchemy.exc import IntegrityError

from backend.db.models import Product, SessionLocal, User
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging

log = logging.getLogger(__name__)
settings = get_settings()
setup_logging()

# ──────────────────────────────────────────────────────────────────────────────
# CLI args
# ──────────────────────────────────────────────────────────────────────────────


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import Amazon order receipts via IMAP")
    p.add_argument("--email", required=True, help="RecallGuard user email to attach products to")
    p.add_argument("--imap-user", required=True, help="IMAP username (Gmail address)")
    p.add_argument("--imap-pass", required=True, help="IMAP password or App Password")
    p.add_argument("--imap-host", default="imap.gmail.com", help="IMAP server hostname")
    p.add_argument("--since", type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d").date(), required=True)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse receipts and log UPCs but do NOT write any products to DB",
    )
    return p.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────────
# Amazon parsing helpers
# ──────────────────────────────────────────────────────────────────────────────

ASIN_RE = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})")
UPC_RE = re.compile(r"\bUPC(?:\s*Code)?:?\s*([\d]{12,14})")
EAN_RE = re.compile(r"\bEAN(?:\s*Code)?:?\s*([\d]{13,14})")


def extract_codes(html: str) -> list[str]:
    """Return list of ASIN/UPC/EAN codes found in the receipt HTML."""
    soup = bs4.BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    codes: list[str] = []
    # ASINs from links
    for m in ASIN_RE.finditer(html):
        codes.append(m.group(1))

    # UPC / EAN from plain text
    codes.extend(m.group(1) for m in UPC_RE.finditer(text))
    codes.extend(m.group(1) for m in EAN_RE.finditer(text))
    return list(set(codes))  # dedupe


# ──────────────────────────────────────────────────────────────────────────────
# IMAP helpers
# ──────────────────────────────────────────────────────────────────────────────


def imap_connect(host: str, user: str, pwd: str) -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL(host)
    conn.login(user, pwd)
    return conn


def search_amazon_orders(conn: imaplib.IMAP4_SSL, since: dt.date) -> list[bytes]:
    conn.select("INBOX")
    date_str = since.strftime("%d-%b-%Y")
    typ, data = conn.search(None, f'(FROM "order-update@amazon.com" SINCE {date_str})')
    if typ != "OK":
        raise RuntimeError("IMAP search failed")
    return data[0].split()


def fetch_email(conn: imaplib.IMAP4_SSL, msg_id: bytes) -> str:
    typ, data = conn.fetch(msg_id, "(RFC822)")
    if typ != "OK":
        raise RuntimeError(f"Failed to fetch email id {msg_id}")
    return data[0][1].decode("utf-8", errors="replace")


# ──────────────────────────────────────────────────────────────────────────────
# DB insertion
# ──────────────────────────────────────────────────────────────────────────────


def upsert_products(user: User, codes: list[str], dry_run: bool) -> int:
    inserted = 0
    if dry_run:
        log.info("[DRY-RUN] Would insert %s products for %s", len(codes), user.email)
        return 0

    with SessionLocal() as db:
        for code in codes:
            prod = Product(
                identifier=code,
                user_id=user.id,
                source="EMAIL",
                metadata={"origin": "amazon"},
            )
            db.add(prod)
            try:
                db.commit()
                inserted += 1
            except IntegrityError:
                db.rollback()  # duplicate for this user
    return inserted


# ──────────────────────────────────────────────────────────────────────────────
# Main logic
# ──────────────────────────────────────────────────────────────────────────────


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)

    with SessionLocal() as db:
        user = db.query(User).filter_by(email=args.email).one_or_none()
        if user is None:
            log.error("No RecallGuard user with email %s", args.email)
            sys.exit(1)

    conn = imap_connect(args.imap_host, args.imap_user, args.imap_pass)

    msg_ids = search_amazon_orders(conn, args.since)
    log.info("Found %s Amazon emails since %s", len(msg_ids), args.since)

    all_codes: list[str] = []
    for msg_id in msg_ids:
        raw_email = fetch_email(conn, msg_id)
        msg = email.message_from_string(raw_email)
        subj = str(make_header(decode_header(msg["Subject"])))
        #  decode payload (multipart / html)
        body_html = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/html":
                    body_html = part.get_payload(decode=True).decode(errors="replace")
                    break
        else:
            body_html = msg.get_payload(decode=True).decode(errors="replace")

        codes = extract_codes(body_html)
        if codes:
            log.debug("Email %s (%s) -> %s codes", msg_id.decode(), subj, len(codes))
            all_codes.extend(codes)

    all_codes = list(set(all_codes))
    log.info("Total unique codes extracted: %s", len(all_codes))
    inserted = upsert_products(user, all_codes, args.dry_run)

    log.info("Inserted %s new products for %s", inserted, user.email)
    conn.logout()


if __name__ == "__main__":  # pragma: no cover
    main()
