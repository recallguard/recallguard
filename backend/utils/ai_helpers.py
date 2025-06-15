"""AI helper functions."""


def summarize_text(text: str) -> str:
    """Return a short summary of the text."""
    lines = text.strip().splitlines()
    return lines[0] if lines else ""

