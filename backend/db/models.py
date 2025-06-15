"""SQLAlchemy models for RecallGuard."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Recall(Base):
    __tablename__ = "recalls"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    product = Column(String, nullable=False)
    hazard = Column(String)
    recall_date = Column(Date)
    details_url = Column(String)
    raw_json = Column(Text)

    alerts = relationship("Alert", back_populates="recall")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Recall source={self.source} product={self.product} recall_date={self.recall_date}>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("UserItem", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<User email={self.email}>"


class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_name = Column(String, nullable=False)

    user = relationship("User", back_populates="items")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<UserItem {self.item_name}>"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recall_id = Column(Integer, ForeignKey("recalls.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    recall = relationship("Recall", back_populates="alerts")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Alert user_id={self.user_id} recall_id={self.recall_id}>"
