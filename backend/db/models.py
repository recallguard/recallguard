"""Data models for RecallGuard."""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str


@dataclass
class Product:
    id: int
    name: str
    user_id: int

