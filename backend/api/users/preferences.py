"""backend/api/users/preferences.py
==================================
Endpoints for reading/updating per‑user settings such as notification
frequency, preferred alert channels, and which recall sources to monitor.

Routes
------
* **GET  /preferences**  – Return the current user’s preference object.
* **PUT  /preferences**  – Replace the preference object in full.
* **PATCH /preferences** – Partial update (only the fields provided).

The table lives on the `User` model as a JSON column (`preferences`) to
keep schema churn minimal.  Validation is enforced through a Pydantic
schema and the column is never returned raw – always normalised through
`UserPreferencesOut`.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from backend.db.models import SessionLocal, User
from backend.utils.config import get_settings
from backend.api.users.auth import get_current_user

log = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/preferences", tags=["preferences"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ChannelPrefs(BaseModel):
    email: bool = Field(True, description="Send alert summaries via e‑mail")
    sms: bool = Field(False, description="Send SMS alerts (Twilio)")
    push: bool = Field(False, description="Enable web‑push notifications")


class SourcePrefs(BaseModel):
    cpsc: bool = True
    fda: bool = True
    usda: bool = True
    nhtsa: bool = True
    misc: bool = True


class UserPreferencesIn(BaseModel):
    channels: Optional[ChannelPrefs] = None
    sources: Optional[SourcePrefs] = None
    digest_hour_utc: Optional[int] = Field(
        None,
        ge=0,
        le=23,
        description="Hour of day (UTC) to send daily digest e‑mails; null means immediate",
    )

    @validator("digest_hour_utc")
    def _validate_hour(cls, v):  # noqa: N805
        if v is not None and not 0 <= v <= 23:
            raise ValueError("digest_hour_utc must be between 0 and 23")
        return v


class UserPreferencesOut(UserPreferencesIn):
    id: int = Field(..., description="User ID owning these preferences")
    updated_at: dt.datetime = Field(..., description="Last update timestamp (UTC)")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_prefs_dict(user: User) -> dict[str, Any]:
    """Return the user.preferences JSON, falling back to defaults."""
    defaults = UserPreferencesIn().dict(exclude_none=True)
    return {**defaults, **(user.preferences or {})}


def _upsert_prefs(db, user: User, new_prefs: dict[str, Any]) -> None:
    """Persist the merged JSON dict into the User row."""
    stmt = (
        update(User)
        .where(User.id == user.id)
        .values(preferences=new_prefs, preferences_updated_at=dt.datetime.utcnow())
    )
    db.execute(stmt)
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("", response_model=UserPreferencesOut)
async def get_preferences(current: User = Depends(get_current_user)):
    """Return the currently authenticated user’s preferences."""
    prefs = _get_prefs_dict(current)
    return UserPreferencesOut(
        id=current.id,
        updated_at=current.preferences_updated_at or current.created_at,
        **prefs,
    )


@router.put("", response_model=UserPreferencesOut)
async def replace_preferences(
    payload: UserPreferencesIn,
    current: User = Depends(get_current_user),
):
    """Replace the entire preferences object."""
    new_prefs = payload.dict(exclude_unset=True, exclude_none=True)
    with SessionLocal() as db:
        try:
            _upsert_prefs(db, current, new_prefs)
            current.preferences = new_prefs  # refresh in‑memory
        except SQLAlchemyError as exc:
            log.error("Failed to save prefs: %s", exc, exc_info=exc)
            raise HTTPException(status_code=500, detail="Failed to save preferences")
    return await get_preferences(current)  # type: ignore[arg-type]


@router.patch("", response_model=UserPreferencesOut)
async def patch_preferences(
    payload: UserPreferencesIn,
    current: User = Depends(get_current_user),
):
    """Update only the provided fields (merge)."""
    existing = _get_prefs_dict(current)
    patch = payload.dict(exclude_unset=True, exclude_none=True)

    # Deep merge channels/sources if provided
    if "channels" in patch and "channels" in existing:
        patch["channels"] = {**existing["channels"], **patch["channels"]}
    if "sources" in patch and "sources" in existing:
        patch["sources"] = {**existing["sources"], **patch["sources"]}

    merged = {**existing, **patch}

    with SessionLocal() as db:
        try:
            _upsert_prefs(db, current, merged)
            current.preferences = merged
        except SQLAlchemyError as exc:
            log.error("Failed to update prefs: %s", exc, exc_info=exc)
            raise HTTPException(status_code=500, detail="Failed to update preferences")
    return await get_preferences(current)  # type: ignore[arg-type]
