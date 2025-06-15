"""Configuration utilities."""
import os


def get_db_path() -> str:
    return os.getenv("RECALLGUARD_DB", "recallguard.db")

