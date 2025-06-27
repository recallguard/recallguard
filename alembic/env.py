"""
Alembic migration environment
-----------------------------
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# --- PATCH START: Fix Alembic compare_type error ---
from alembic.autogenerate import comparators
import sqlalchemy.dialects.postgresql as pg

@comparators.dispatch_for("column")
def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type, **kwargs):
    # Treat JSON and JSONB as equivalent for schema comparison
    json_types = (pg.JSON, pg.JSONB)
    if isinstance(inspected_type, json_types) and isinstance(metadata_type, json_types):
        return False
    return None  # fallback to default comparison for all other types
# --- PATCH END ---

# Load environment variables
load_dotenv()

# Append project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

# Import your models and extract metadata
from backend.db import models as db_models  # noqa: E402
target_metadata = db_models.metadata

# Set Alembic configuration
config = context.config
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL not set in environment (.env)")
config.set_main_option("sqlalchemy.url", db_url)

# Set up logging
fileConfig(config.config_file_name, disable_existing_loggers=False)

# Run migrations (offline and online)
def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# Entrypoint
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
