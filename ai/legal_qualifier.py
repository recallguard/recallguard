"""Determine if a recall should include a legal referral."""
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "prompt_templates" / "legal_referral_prompt.txt"


def needs_referral(notice: str) -> bool:
    TEMPLATE_PATH.read_text()
    return "injury" in notice.lower()

