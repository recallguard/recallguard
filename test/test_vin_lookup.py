"""
tests/test_vin_lookup.py
========================
Integration-style unit tests for the VIN lookup endpoint
(`backend/api/products/vin_lookup.py`).

We patch the outbound NHTSA call so tests run offline and deterministically.

Run with::

    pytest -q tests/test_vin_lookup.py
"""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Harness setup – in-memory SQLite app instance
# ---------------------------------------------------------------------------

from backend.db.models import Base, User, Product  # noqa: E402  (local import after PYTHONPATH set)

from backend.main import create_app  # your FastAPI factory

# Use in-memory SQLite so we don’t touch a real DB
SQL_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(SQL_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)  # type: ignore[var-annotated]
Base.metadata.create_all(engine)


def override_get_db() -> Session:  # FastAPI dependency override
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides["get_db"] = override_get_db
client = TestClient(app, raise_server_exceptions=False)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def seed_user() -> dict[str, Any]:
    """Insert a demo user and return its auth header."""
    with TestingSessionLocal() as db:
        user = User(email="demo@example.com", hashed_password="$2b$12$abcdefghijk", stripe_customer_id=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    # We bypass auth here: FastAPI dependency for `get_current_user`
    # is patched to always return this user
    app.dependency_overrides["get_current_user"] = lambda: user  # type: ignore[assignment]
    return {"Authorization": "Bearer dummy.jwt.token"}


VALID_VIN = "1HGCM82633A004352"  # Honda Accord - valid checksum


def nhtsa_stub_json(vin: str) -> dict[str, Any]:
    """Craft the minimal JSON structure the endpoint expects."""
    return {
        "Results": [
            {
                "Make": "HONDA",
                "Model": "Accord",
                "ModelYear": "2003",
                "VIN": vin,
                "ErrorCode": "0",
                "ErrorText": "",
            }
        ]
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "vin,expected_status",
    [
        (VALID_VIN, status.HTTP_201_CREATED),
        ("1HGCM82633A004351", status.HTTP_422_UNPROCESSABLE_ENTITY),  # bad checksum
        ("TOO-SHORT", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
def test_vin_lookup_responses(seed_user, vin, expected_status):
    """Validate basic response codes for various VIN inputs."""
    json_body = {"vin": vin}

    async def fake_nhtsa_call(*_args, **_kwargs):
        return nhtsa_stub_json(vin)

    with patch("backend.api.products.vin_lookup._decode_vin", new=AsyncMock(side_effect=fake_nhtsa_call)):
        resp = client.post("/products/vin", json=json_body, headers=seed_user)

    assert resp.status_code == expected_status

    if resp.status_code == status.HTTP_201_CREATED:
        # The product should now exist in DB
        with TestingSessionLocal() as db:
            prod = db.query(Product).filter_by(identifier=vin).one_or_none()
            assert prod is not None
            assert prod.metadata.get("make") == "HONDA"


def test_duplicate_vin_returns_conflict(seed_user):
    """Posting the *same* valid VIN twice should hit 409 Conflict."""
    body = {"vin": VALID_VIN}

    async def fake_nhtsa_call(*_args, **_kwargs):
        return nhtsa_stub_json(VALID_VIN)

    with patch("backend.api.products.vin_lookup._decode_vin", new=AsyncMock(side_effect=fake_nhtsa_call)):
        # 1st insert – should succeed
        first = client.post("/products/vin", json=body, headers=seed_user)
        assert first.status_code == status.HTTP_201_CREATED

        # 2nd insert – should conflict
        second = client.post("/products/vin", json=body, headers=seed_user)
        assert second.status_code == status.HTTP_409_CONFLICT
        assert "already tracking" in second.json()["detail"].lower()
