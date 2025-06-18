"""Utilities for AI-powered recall summaries."""
from __future__ import annotations

import os
from typing import Tuple

import openai


SYSTEM_PROMPT = (
    "You are a helpful assistant generating brief recall summaries. "
    "Provide two sentences, no more than 50 words total, explaining the hazard "
    "in plain English. Then provide a single imperative sentence beginning with "
    "'Next:' advising the user what to do."
)


def summarize_recall(name: str, hazard: str, classification: str | None = None) -> Tuple[str, str]:
    """Return a short summary and next steps for a recall."""
    api_key = os.getenv("OPENAI_API_KEY")
    user_content = f"Product: {name}\nHazard: {hazard}\nClassification: {classification or ''}"
    if api_key:
        client = openai.OpenAI(api_key=api_key)
        try:
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_content}],
                temperature=0.2,
            )
            message = resp.choices[0].message.content.strip()
        except Exception:
            message = f"{name} may pose a hazard: {hazard}." " Next: Follow official guidance."
    else:
        message = f"{name} may pose a hazard: {hazard}." " Next: Follow official guidance."
    # split into summary and next steps
    if "Next:" in message:
        summary_text, next_part = message.split("Next:", 1)
        summary_text = summary_text.strip()
        next_steps = "Next:" + next_part.strip()
    else:
        lines = [line.strip() for line in message.splitlines() if line.strip()]
        if lines and lines[-1].lower().startswith("next:"):
            summary_text = " ".join(lines[:-1])
            next_steps = lines[-1]
        else:
            summary_text = message
            next_steps = ""
    return summary_text, next_steps
