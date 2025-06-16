"""Data models for RecallGuard."""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    created_at: str


@dataclass
class Product:
    id: int
    name: str
    user_id: int

