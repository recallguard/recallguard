"""Import purchase data from emails."""


def parse_email(content: str) -> list:
    """Parse an email and return a list of products found."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return lines

