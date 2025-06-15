"""Tools to summarize recall notices."""
from pathlib import Path
from backend.utils.ai_helpers import summarize_text

TEMPLATE_PATH = Path(__file__).parent / "prompt_templates" / "summary_template.txt"


def summarize(notice: str) -> str:
    template = TEMPLATE_PATH.read_text()
    filled = template.replace("{notice}", notice)
    return summarize_text(filled)

