"""backend/api/products/vision_scan.py – Add product via image barcode scan
==============================================================================

This FastAPI router lets an authenticated user upload a **photo** of a
physical product. The service attempts to extract a barcode (UPC/EAN) from
the image and, if successful, creates—or re-uses—the corresponding
`Product` row and links it to the current user so that RecallGuard can
monitor future recalls.
"""
from __future__ import annotations

import io
import os
from typing import Optional

import httpx
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from PIL import Image
from pyzbar.pyzbar import decode as decode_barcodes
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.utils.db import get_db
from backend.api.users.auth import get_current_user
from backend.db.models import Product as DBProduct, User as DBUser
from backend.utils.logging import get_logger
from backend.api.products.schemas import ProductOut

logger = get_logger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


def _validate_upc_ean(code: str) -> str:
    """Return a cleaned 12- or 13-digit code if checksum passes, else ValueError."""
    digits = "".join(filter(str.isdigit, code))
    if len(digits) not in (12, 13):
        raise ValueError("Barcode must be 12 or 13 digits")
    # EAN-13 checksum (works for UPC-A when padded)
    total = sum(
        (3 if i % 2 else 1) * int(n)
        for i, n in enumerate(digits[:-1])
    )
    check_digit = (10 - (total % 10)) % 10
    if check_digit != int(digits[-1]):
        raise ValueError("Invalid UPC/EAN checksum")
    return digits


def _decode_local(image: Image.Image) -> Optional[str]:
    """Try local barcode extraction using pyzbar."""
    try:
        for result in decode_barcodes(image):
            if result.type in {"EAN13", "EAN8", "UPCA"}:
                code = result.data.decode("utf-8")
                try:
                    return _validate_upc_ean(code)
                except ValueError:
                    continue
    except Exception as exc:
        logger.warning("Local barcode decode failed: %s", exc)
    return None


def _decode_google_vision(image_bytes: bytes) -> Optional[str]:
    """Fallback to Google Cloud Vision API if GCP_VISION_CREDENTIALS is set."""
    key = os.getenv("GCP_VISION_CREDENTIALS")
    if not key:
        return None

    endpoint = "https://vision.googleapis.com/v1/images:annotate"
    payload = {
        "requests": [
            {
                "image": {"content": image_bytes.decode("latin1").encode("base64")},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }
    try:
        resp = httpx.post(endpoint, params={"key": key}, json=payload, timeout=10)
        resp.raise_for_status()
        annotations = resp.json()["responses"][0].get("textAnnotations", [])
        for ann in annotations:
            try:
                return _validate_upc_ean(ann["description"].strip())
            except ValueError:
                continue
    except Exception as exc:
        logger.warning("Vision API decode failed: %s", exc)

    return None


@router.post(
    "/vision",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductOut,
    summary="Add product by photo barcode scan",
)
async def add_product_via_vision(
    file: UploadFile = File(..., description="JPEG/PNG image containing a barcode"),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Extract a barcode from the uploaded image and link the product."""
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG or PNG images are accepted",
        )

    image_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid image file")

    # Step 1: local decode
    code = _decode_local(image)

    # Step 2: fall back to Google Vision
    if code is None:
        code = _decode_google_vision(image_bytes)

    if not code:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No valid barcode found")

    try:
        product = db.query(DBProduct).filter_by(upc=code).one_or_none()
        if product is None:
            product = DBProduct(upc=code)
            db.add(product)
            db.flush()  # get PK for association

        if product not in current_user.products:
            current_user.products.append(product)
        else:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Product already tracked by user",
            )

        db.commit()
        db.refresh(product)

    except SQLAlchemyError as exc:
        logger.error("DB error linking product: %s", exc)
        db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error",
        )

    return ProductOut.from_orm(product)
