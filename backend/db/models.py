from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    PrimaryKeyConstraint,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("email_opt_in", Integer, nullable=False, server_default=text("0")),
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
    Column("summary_text", Text),
    Column("next_steps", Text),
    Column("remedy_updates", JSONB, server_default=text("'[]'::jsonb")),
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

subscriptions = Table(
    "subscriptions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("recall_source", String, nullable=False),
    Column("product_query", String, nullable=False),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

sent_notifications = Table(
    "sent_notifications",
    metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("recall_id", String, primary_key=True),
)

user_items = Table(
    "user_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("upc", String, nullable=False),
    Column("label", String),
    Column("profile", String, nullable=False, server_default=text("'self'")),
    Column("added_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

push_tokens = Table(
    "push_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("token", String, nullable=False),
    Column("added_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    PrimaryKeyConstraint("id"),
    UniqueConstraint("user_id", "token")
)

email_unsub_tokens = Table(
    "email_unsub_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("token", String, nullable=False, unique=True),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

api_keys = Table(
    "api_keys",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("org_name", String, nullable=False),
    Column("key", String, nullable=False, unique=True),
    Column("plan", String, server_default=text("'free'")),
    Column("monthly_quota", Integer, server_default=text("5000")),
    Column("requests_this_month", Integer, server_default=text("0")),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

channel_subs = Table(
    "channel_subs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("platform", String),
    Column("channel_id", String, nullable=False),
    Column("query", String, nullable=False),
    Column("source", String, server_default=text("'CPSC'")),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

webhooks = Table(
    "webhooks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("api_key_id", Integer, ForeignKey("api_keys.id")),
    Column("url", String, nullable=False),
    Column("query", String),
    Column("source", String),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

invites = Table(
    "invites",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("recall_id", String),
    Column("sent_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

stripe_customers = Table(
    "stripe_customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), unique=True),
    Column("stripe_customer_id", String),
    Column("subscription_id", String),
    Column("plan", String, server_default=text("'free'")),
    Column("quota", Integer, server_default=text("100")),
    Column("seats", Integer, server_default=text("1")),
)
