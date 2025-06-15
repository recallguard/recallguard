"""Very simple authentication placeholder."""


def login(username: str, password: str) -> bool:
    """Return True if credentials match hardcoded example."""
    return username == "admin" and password == "secret"

