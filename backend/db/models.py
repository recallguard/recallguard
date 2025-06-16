from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Text, ForeignKey, PrimaryKeyConstraint
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", String, nullable=False),
)

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("user_id", Integer, ForeignKey("users.id")),
)

recalls = Table(
    "recalls",
    metadata,
    Column("id", String, nullable=False),
    Column("product", String, nullable=False),
    Column("hazard", Text),
    Column("recall_date", String),
    Column("source", String, nullable=False),
    Column("fetched_at", String, nullable=False),
    PrimaryKeyConstraint("id", "source"),
)

alerts = Table(
    "alerts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("recall_id", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("sent_at", String),
    Column("read_at", String),
    Column("error", Text),
)
