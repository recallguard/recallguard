"""backend/api/products/vin_lookup.py
===================================
Decode a VIN (Vehicle Identification Number) using the NHTSA API
and link it as a Product for the authenticated user.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.db import models as m
from backend.utils.db import get_db
from backend.api.users.auth import get_current_user
from backend.utils.config import get_settings

router = APIRouter(prefix="/products", tags=["products"])
settings = get_settings()

NHTSA_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/"
    "decodevinvaluesextended/{vin}?format=json"
)

# VIN must be 17 chars, letters+digits (no I/O/Q)
VIN_REGEX = r"^[A-HJ-NPR-Z0-9]{17}$"


class VINIn(BaseModel):
    # Annotated str with Pydantic v2 Field
    vin: Annotated[
        str,
        Field(
            min_length=17,
            max_length=17,
            pattern=VIN_REGEX,
            description="17-character VIN (no I/O/Q)",
        ),
    ]

    @field_validator("vin")
    @classmethod
    def uppercase_and_checksum(cls, v: str) -> str:
        vin = v.upper()
        if settings.enforce_vin_checksum and not _is_valid_vin(vin):
            raise ValueError("Invalid VIN checksum")
        return vin


class ProductOut(BaseModel):
    id: int
    identifier: str
    kind: str
    display_name: str
    created_at: str

    model_config = {"populate_by_name": True, "from_attributes": True}


def _is_valid_vin(vin: str) -> bool:
    translit = {**{str(i): i for i in range(10)},
                **dict(zip("ABCDEFGHJKLMNPRSTUVWXYZ",
                           [1,2,3,4,5,6,7,8,1,2,3,4,5,7,9,2,3,4,5,6,7,8,9]))}
    weights = [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]
    total = sum(translit[ch] * w for ch, w in zip(vin, weights))
    check = (10 - (total % 10)) % 10
    expected = "X" if check == 10 else str(check)
    return vin[8] == expected


async def _decode_vin(vin: str) -> Dict[str, Any]:
    url = NHTSA_URL.format(vin=vin)
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Failed to reach NHTSA")
        j = r.json()
    try:
        return j["Results"][0]
    except (KeyError, IndexError):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Malformed NHTSA response")


@router.post("/vin", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def add_vehicle_by_vin(
    payload: VINIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    vin = payload.vin

    # 1) Check if already tracked
    exists = (
        db.query(m.Product)
        .join(m.Product.owners)
        .filter(m.User.id == current_user.id, m.Product.identifier == vin)
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "You already track this vehicle")

    # 2) Decode via NHTSA
    decoded = await _decode_vin(vin)
    year = decoded.get("ModelYear") or "Unknown"
    make = decoded.get("Make") or "Unknown"
    model = decoded.get("Model") or "Unknown"
    name = f"{year} {make} {model}"

    # 3) Upsert a shared Product row
    product = db.query(m.Product).filter_by(identifier=vin).first()
    if not product:
        product = m.Product(identifier=vin, kind="vin", display_name=name)
        db.add(product)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "VIN exists—retry")

    # 4) Link to user
    current_user.products.append(product)
    db.commit()
    db.refresh(product)

    return ProductOut.from_orm(product)
