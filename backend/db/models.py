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
