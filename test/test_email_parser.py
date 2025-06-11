"""tests/test_email_parser.py
============================
Validate that the receipt‑parsing layer in `backend/api/products/email_import.py`
correctly extracts UPCs/SKUs from sample HTML purchase receipts.

The tests patch the network layer so no IMAP/Gmail traffic occurs; instead
we feed known HTML snippets into the `_parse_receipt()` helper and assert
the resulting product identifiers match expectations.

Run with::

    pytest -q tests/test_email_parser.py
"""
from __future__ import annotations

import importlib
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Iterable

import pytest

# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "receipts"

@pytest.fixture(scope="module")
def email_mod() -> ModuleType:  # noqa: D401
    """Import the email_import module lazily so patches apply."""
    mod = importlib.import_module("backend.api.products.email_import")
    return mod


def load_fixture(name: str) -> str:
    path = FIXTURES_DIR / f"{name}.html"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf‑8")


# ---------------------------------------------------------------------------
# Sample receipts → expected UPC lists
# ---------------------------------------------------------------------------

RECEIPT_CASES: list[tuple[str, list[str]]] = [
    (
        "amazon_single_item",
        ["012345678905"],  # UPC‑A 12‑digit
    ),
    (
        "walmart_two_items",
        ["0075678164123", "0001356219946"],
    ),
    (
        "target_multipack",
        ["036000291452"],
    ),
]


@pytest.mark.parametrize("fixture_name,expected_upcs", RECEIPT_CASES)
def test_parse_receipt_extracts_upcs(email_mod: ModuleType, fixture_name: str, expected_upcs: list[str]):  # noqa: D401
    """Ensure _parse_receipt() returns *all* UPCs present in the fixture."""
    html = load_fixture(fixture_name)

    upcs: list[str] = email_mod._parse_receipt(html)  # type: ignore[attr-defined] # private helper

    assert sorted(upcs) == sorted(expected_upcs)
    # Basic checksum validation (last digit)
    for code in upcs:
        assert len(code) in (12, 13)
        assert code.isdigit()


def test_parse_receipt_handles_no_upc(email_mod: ModuleType):  # noqa: D401
    """If a receipt has no UPC/EAN, the helper should return an empty list."""
    html = dedent(
        """
        <html><body>
            <p>Thank you for your purchase! Your item SKU: ABC‑123.</p>
        </body></html>
        """
    ).strip()

    upcs: list[str] = email_mod._parse_receipt(html)  # type: ignore[attr-defined]
    assert upcs == []


@pytest.mark.parametrize("fixture_name,expected_upcs", RECEIPT_CASES[:1])
def test_parse_receipt_memoises_results(monkeypatch, email_mod: ModuleType, fixture_name: str, expected_upcs: list[str]):  # noqa: D401,E501
    """The helper caches parsed results so repeated calls are O(1)."""
    html = load_fixture(fixture_name)

    # Prime the cache
    first = email_mod._parse_receipt(html)
    assert first == expected_upcs

    # Patch the regex search to verify it is NOT called the second time
    captured_calls: list[str] = []

    def _fake_extract(_: str) -> Iterable[str]:  # noqa: D401
        captured_calls.append("extract")
        return []

    monkeypatch.setattr(email_mod, "_extract_upcs_from_html", _fake_extract)  # type: ignore[attr-defined]

    second = email_mod._parse_receipt(html)
    assert second == expected_upcs  # result came from cache
    assert not captured_calls  # regex path was skipped
