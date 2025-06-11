"""
ai/summarizer.py
================
Turn verbose recall bulletins from CPSC / FDA / USDA / NHTSA into a concise
plain-English summary (≤ 45 words) for RecallGuard email alerts.

Design notes
------------
* Template-driven: loads Jinja2 prompt text from
  `ai/prompt_templates/summary_template.txt`.
* Retries once if the model exceeds the word-limit.
* Async-friendly and robust to transient OpenAI rate limits.
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Final

import openai
from jinja2 import Template

from backend.utils.config import get_settings
from backend.utils.logging import logging

settings = get_settings()
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TEMPLATE_PATH: Final = Path(__file__).with_suffix("").parent / "prompt_templates" / "summary_template.txt"
_WORD_LIMIT: Final = 45
MODEL: Final = settings.OPENAI_COMPLETIONS_MODEL or "gpt-3.5-turbo-0125"

# compile regex once
_WORD_RE = re.compile(r"\b\w+\b", re.U)


def _word_count(text: str) -> int:
    """A quick word count using regex (handles punctuation)."""
    return len(_WORD_RE.findall(text))


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def _load_template() -> Template:
    content = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return Template(content, trim_blocks=True, lstrip_blocks=True)


TEMPLATE: Template = _load_template()


def _build_prompt(bulletin: str) -> str:
    """Render the Jinja2 prompt with the bulletin text."""
    return TEMPLATE.render(bulletin_text=bulletin.strip())


# ---------------------------------------------------------------------------
# OpenAI call + retry
# ---------------------------------------------------------------------------

async def _chat_complete(prompt: str) -> str:
    """Call OpenAI ChatCompletion API with sensible defaults."""
    response = await openai.ChatCompletion.acreate(
        model=MODEL,
        temperature=0.4,
        max_tokens=120,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()


async def summarise_bulletin(bulletin_text: str) -> str:
    """
    Return a ≤ 45-word consumer-friendly summary of `bulletin_text`.
    """
    prompt = _build_prompt(bulletin_text)

    # --- try once, then retry if length > word-limit ------------------------
    for attempt in (1, 2):
        try:
            summary = await _chat_complete(prompt)
        except openai.error.RateLimitError as exc:
            # back-off then retry (max 2 attempts)
            log.warning("OpenAI rate-limited; retrying in 3 s (attempt %s/2)", attempt)
            await asyncio.sleep(3)
            continue

        wc = _word_count(summary)
        if wc <= _WORD_LIMIT:
            return summary

        log.debug("Summary too long (%s words). Retrying with stricter prompt.", wc)
        prompt = (
            "Rewrite the summary below in under 45 words, plain English only:\n\n"
            f"---\n{summary}\n---"
        )

    # last resort: truncate
    words = _WORD_RE.findall(summary)
    truncated = " ".join(words[:_WORD_LIMIT])
    log.warning("Returning truncated summary: %s …", truncated)
    return truncated
