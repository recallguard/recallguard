"""backend/api/products/manual_entry.py – Manual product registration endpoint

Allows an authenticated user to add an item (UPC, VIN, or generic
identifier) to their RecallGuard watch-list when the product wasn’t picked
up automatically via email import or vision scan.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr, validator
from sqlalchemy.orm import Session

from backend.db import models
from backend.utils.db import get_db  # our new DB helper
from backend.api.users.auth import get_current_user  # OAuth2/JWT dependency

router = APIRouter(prefix="/products", tags=["products"])

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ManualProductIn(BaseModel):
    """User-supplied product details."""

    identifier: constr(strip_whitespace=True, min_length=3, max_length=64)
    brand: constr(strip_whitespace=True, min_length=2, max_length=64) | None = None
    description: constr(strip_whitespace=True, min_length=2, max_length=128) | None = None

    @validator("identifier", pre=True)
    def normalise(cls, v: str) -> str:
        # normalise weird nbsp chars
        return v.replace(" ", " ").strip()


class ProductOut(BaseModel):
    id: int
    identifier: str
    brand: str | None
    description: str | None

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _canonical_identifier(identifier: str) -> str:
    """Return a stable comparison key (upper-case, no whitespace)."""
    return "".join(identifier.upper().split())


# ---------------------------------------------------------------------------
# Route handler
# ---------------------------------------------------------------------------

@router.post("/manual", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def add_manual_product(
    payload: ManualProductIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Register a new *manual* product for the current user.

    Logic:
    1. Canonicalise the identifier for consistent matching.
    2. Check whether the *user* already tracks this identifier → 409 Conflict.
    3. Lookup a global `Product` row.  Re-use if present, else create.
    4. Associate the product with the current user and commit.
    """
    key = _canonical_identifier(payload.identifier)

    # Step 1: Early duplicate check scoped to the current user
    dup = (
        db.query(models.Product)
        .filter(
            models.Product.user_id == current_user.id,
            models.Product.identifier == key,
        )
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already track this product.",
        )

    # Step 2: Fetch or create the shared Product row
    product = db.query(models.Product).filter_by(identifier=key).first()
    if product is None:
        product = models.Product(
            identifier=key,
            brand=payload.brand,
            description=payload.description,
        )
        db.add(product)
        db.flush()  # obtain PK without full commit yet

    # Step 3: Associate with the current user
    current_user.products.append(product)

    db.commit()
    db.refresh(product)
    return product
