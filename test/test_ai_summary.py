"""Unit tests for the AI‑powered summariser (ai/summarizer.py).

We *mock* the underlying OpenAI call so that the tests run offline and are
fully deterministic.

Run with::

    pytest -q tests/test_ai_summary.py
"""
from __future__ import annotations

import importlib
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RAW_RECALL = dedent(
    """
    The U.S. Consumer Product Safety Commission (CPSC) announced today that
    XYZ Corp. is recalling 42,000 lithium‑powered hoverboards sold between
    January 2022 and April 2023.  The battery pack can overheat, posing fire
    and burn hazards.  The company has received 14 reports of overheating,
    including two house fires and $150,000 in property damage.  Consumers
    should immediately stop using the hoverboards and contact XYZ Corp. for
    a free replacement battery pack and installation.
    """
)

# Summaries should be short (\<= 400 chars) and mention keyword(s)
MAX_LEN = 400
KEY_WORDS = [
    "overheat",
    "fire",
    "burn",
]


@pytest.fixture(scope="module")
def summarizer() -> ModuleType:
    """Import the module only once per session."""
    return importlib.import_module("ai.summarizer")


@pytest.mark.asyncio
async def test_summarise_happy_path(summarizer):
    """The helper should call OpenAI and return its text."""

    # Arrange: patch the low‑level ai_helpers.call_chat() coroutine
    fake_response = "XYZ hoverboards recalled: battery packs overheat causing fires; stop use and request free replacement."
    with patch(
        "ai.summarizer.call_chat", new=AsyncMock(return_value=fake_response)
    ) as mock_call:
        # Act
        summary = await summarizer.summarise(RAW_RECALL)

    # Assert
    mock_call.assert_awaited_once()
    assert summary == fake_response
    assert len(summary) <= MAX_LEN
    for kw in KEY_WORDS:
        assert kw in summary.lower()


@pytest.mark.asyncio
async def test_summarise_fallback_on_error(summarizer):
    """If the OpenAI call fails, summarise() returns a trimmed fallback."""
    # Simulate an exception from the API
    with patch(
        "ai.summarizer.call_chat", new=AsyncMock(side_effect=RuntimeError("API down"))
    ):
        summary = await summarizer.summarise(RAW_RECALL)

    # Fallback should simply truncate + ellipsis
    assert summary.endswith("…")
    assert len(summary) <= MAX_LEN


def test_cli_entrypoint(tmp_path: Path, summarizer):
    """The module exposes a small CLI for manual experimentation."""
    script_path = Path(summarizer.__file__)
    assert script_path.exists(), "summarizer.py file is missing"

    # We don't actually *invoke* the CLI (would fire network calls) – just
    # assert that the module defines a main() for completeness.
    assert hasattr(summarizer, "main"), "summarizer.main() entrypoint missing"
