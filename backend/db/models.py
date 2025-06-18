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
    JSON,
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("email_opt_in", Integer, nullable=False, server_default="0"),
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
    Column("remedy_updates", JSON, server_default="[]"),
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

# Items saved by users via the "My Stuff" locker
user_items = Table(
    "user_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("upc", String, nullable=False),
    Column("label", String),
    Column("profile", String, nullable=False, server_default="self"),
    Column("added_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

# FCM push notification tokens
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

# One-click e-mail unsubscribe tokens
email_unsub_tokens = Table(
    "email_unsub_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("token", String, nullable=False, unique=True),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

# API keys for partner access
api_keys = Table(
    "api_keys",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("org_name", String, nullable=False),
    Column("key", String, nullable=False, unique=True),
    Column("plan", String, server_default="free"),
    Column("monthly_quota", Integer, server_default="5000"),
    Column("requests_this_month", Integer, server_default="0"),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

# Slack/Teams channel subscriptions
channel_subs = Table(
    "channel_subs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("platform", String),
    Column("channel_id", String, nullable=False),
    Column("query", String, nullable=False),
    Column("source", String, server_default="CPSC"),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
)

# Partner webhooks
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
