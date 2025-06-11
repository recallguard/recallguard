"""SQLAlchemy ORM models for RecallGuard
======================================

This file defines the core relational schema used across the backend.
We try to keep the footprint minimal but expressive enough to cover core
use-cases:

* Users      – login credentials, preferences and billing tier.
* Products   – items a user owns/monitors (UPC, VIN, manual, vision).
* Recalls    – normalised ingest of CPSC, FDA, USDA, NHTSA + misc.
* Alerts     – link a user-product pair to a relevant recall event.
* Background – APScheduler jobs (uses its own job store table).

When adding a new model or column, remember to run:
    alembic revision --autogenerate -m "<message>"
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as PgEnum,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

from backend.utils.config import get_settings

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

settings = get_settings()
engine = create_engine(settings.DATABASE_URI, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# ---------------------------------------------------------------------------
# Base declaration
# ---------------------------------------------------------------------------

Base = declarative_base()

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PlanTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class RecallSource(str, enum.Enum):
    CPSC = "cpsc"
    FDA = "fda"
    USDA = "usda"
    NHTSA = "nhtsa"
    MISC = "misc"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Medium(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

# ---------------------------------------------------------------------------
# Association table (many-to-many)
# ---------------------------------------------------------------------------

product_recall_association = Table(
    "product_recalls",
    Base.metadata,
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True),
    Column("recall_id", UUID(as_uuid=True), ForeignKey("recalls.id"), primary_key=True),
    Column(
        "matched_on",
        String(64),
        nullable=False,
        doc="Field that triggered the match (VIN, UPC, etc.)",
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
)

# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    hashed_password: Mapped[bytes] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    plan: Mapped[PlanTier] = mapped_column(PgEnum(PlanTier), default=PlanTier.FREE, nullable=False)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    products: Mapped[list["Product"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner: Mapped[User] = relationship(back_populates="products")

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(128))
    category: Mapped[str | None] = mapped_column(String(64))

    upc: Mapped[str | None] = mapped_column(String(32), index=True)
    serial_number: Mapped[str | None] = mapped_column(String(64), index=True)
    vin: Mapped[str | None] = mapped_column(String(17), index=True)

    notes: Mapped[str | None] = mapped_column(Text)
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    recalls: Mapped[list["Recall"]] = relationship(
        secondary=product_recall_association, back_populates="products"
    )

    __table_args__ = (
        Index("ix_products_multi_id", "upc", "serial_number", "vin"),
    )


class Recall(Base):
    __tablename__ = "recalls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source: Mapped[RecallSource] = mapped_column(PgEnum(RecallSource), nullable=False)

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    hazard: Mapped[str | None] = mapped_column(String(256))
    remedy: Mapped[str | None] = mapped_column(String(256))

    recall_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512))
    image_url: Mapped[str | None] = mapped_column(String(512))

    category: Mapped[str | None] = mapped_column(String(64))
    brand: Mapped[str | None] = mapped_column(String(128))

    products: Mapped[list[Product]] = relationship(
        secondary=product_recall_association, back_populates="recalls"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="recall", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("external_id", "source", name="uq_recall_external_source"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="alerts")

    recall_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recalls.id"), nullable=False)
    recall: Mapped[Recall] = relationship(back_populates="alerts")

    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    product: Mapped[Product | None] = relationship()

    medium: Mapped[Medium] = mapped_column(PgEnum(Medium), default=Medium.EMAIL)
    status: Mapped[AlertStatus] = mapped_column(PgEnum(AlertStatus), default=AlertStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_alert_unique", "user_id", "recall_id", "product_id", unique=True),
    )


def get_base() -> Base:
    """
    Return the declarative Base for Alembic autogeneration.
    """
    return Base


# Expose for convenience
__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "User",
    "Product",
    "Recall",
    "Alert",
    "PlanTier",
    "RecallSource",
    "AlertStatus",
    "Medium",
    "product_recall_association",
    "get_base",
]
