"""Pytest configuration for custom markers."""
import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: integration tests")
