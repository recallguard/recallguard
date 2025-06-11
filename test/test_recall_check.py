"""tests/test_recall_check.py
============================
Unit‑tests for the *matching* logic in ``backend/api/alerts/check_user_items``.

The objective is to confirm that newly‑ingested ``Recall`` rows are correctly
matched to the *products each user owns* and that the corresponding
``Alert`` records are created (once and only once).

The tests run entirely against an **in‑memory SQLite** database so they are
fast, deterministic and do *not* touch the dev/production DB.

Run with::

    pytest -q tests/test_recall_check.py
"""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
from types import ModuleType
from typing import Generator
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# The core models we need
from backend.db import models as m

# Module under test
import importlib

CHECKER_PATH = "backend.api.alerts.check_user_items"
checker: ModuleType | None = None  # populated in fixture

# ---------------------------------------------------------------------------
# Fixtures – in‑memory DB hooked into the checker module
# ---------------------------------------------------------------------------

_ENGINE = create_engine("sqlite:///:memory:", future=True, echo=False)
SessionTest = sessionmaker(bind=_ENGINE, expire_on_commit=False, future=True)  # type: ignore[var‑annotated]

m.Base.metadata.create_all(_ENGINE)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Supply a *transaction‑per‑test* session that rolls back at teardown."""
    session = SessionTest()
    tx = session.begin()
    try:
        yield session
    finally:
        tx.rollback()
        session.close()


@pytest.fixture(autouse=True)
def _patch_sessionlocal(monkeypatch):
    """Patch SessionLocal used by check_user_items to our in‑mem variant."""
    # Import late so we can monkey‑patch before module executes globals
    global checker  # noqa: PLW0603
    checker = importlib.import_module(CHECKER_PATH)

    monkeypatch.setattr(checker, "SessionLocal", SessionTest, raising=True)
    yield


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

UPC = "123456789012"
VIN = "1HGCM82633A004352"


def _create_user(s: Session, email: str = "foo@example.com") -> m.User:  # type: ignore[arg‑type]
    user = m.User(email=email, password_hash="x", stripe_customer_id=None)
    s.add(user)
    s.flush()
    return user


def _create_product(s: Session, owner: m.User, upc: str | None = None, vin: str | None = None) -> m.Product:  # noqa: D401,E501
    product = m.Product(upc=upc, vin=vin)
    s.add(product)
    s.flush()
    # link
    owner.products.append(product)  # type: ignore[attr‑defined]
    s.flush()
    return product


def _create_recall(s: Session, recall_id: str, upc: str | None = None, vin: str | None = None) -> m.Recall:  # noqa: D401,E501
    recall = m.Recall(
        recall_id=recall_id,
        title="Test recall",
        summary="dummy",
        link="https://example.com",
        hazard="Fire",
        remedy="Refund",
        recall_date=dt.date.today(),
        source="TEST",
        upcs=[upc] if upc else None,
        vins=[vin] if vin else None,
    )
    s.add(recall)
    s.flush()
    return recall


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_matching_creates_alert(db_session):
    """A recall that matches a user's product should create one Alert row."""
    with db_session as s:
        user = _create_user(s)
        _create_product(s, user, upc=UPC)
        _create_recall(s, "R‑001", upc=UPC)

    # Act – run the matcher (returns # of alerts inserted)
    inserted = await checker.process_new_recalls()

    # Assert
    with db_session as s:
        alert_count = s.query(m.Alert).filter(m.Alert.user_id == user.id).count()
    assert inserted == 1
    assert alert_count == 1


@pytest.mark.asyncio
async def test_no_duplicate_alerts(db_session):
    """Running the matcher again with no new recalls creates zero alerts."""
    with db_session as s:
        user = _create_user(s, email="dupe@example.com")
        _create_product(s, user, upc=UPC)
        _create_recall(s, "R‑002", upc=UPC)

    # First run – should insert
    first = await checker.process_new_recalls()
    # Second run – nothing new → should return 0
    second = await checker.process_new_recalls()

    assert first == 1 and second == 0


@pytest.mark.asyncio
async def test_non_matching_recall_skipped(db_session):
    """Recalls that don't match any user's products should be ignored."""
    with db_session as s:
        _create_user(s)
        _create_recall(s, "R‑003", upc="000000000000")

    inserted = await checker.process_new_recalls()
    assert inserted == 0
