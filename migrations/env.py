import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1) Load .env so DATABASE_URL is in the process environment
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# 2) Make sure the project root is on sys.path  ( ..\..\ relative to this file )
#    -> adjust if your folder structure differs
# ---------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# ---------------------------------------------------------------------------
# 3) Alembic config & logging
# ---------------------------------------------------------------------------
config = context.config
fileConfig(config.config_file_name)

# Inject DATABASE_URL read from .env into the alembic.ini config
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL not set in environment (.env)")
config.set_main_option("sqlalchemy.url", database_url)

# ---------------------------------------------------------------------------
# 4) Import the MetaData that contains *all* your Core tables
# ---------------------------------------------------------------------------
from backend.db.models import metadata  # <-- this is the object you posted

target_metadata = metadata

# ---------------------------------------------------------------------------
# 5) Standard Alembic offline / online runners
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations without a DB connection (generates SQL only)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
