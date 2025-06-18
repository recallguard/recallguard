from __future__ import annotations

from bs4 import BeautifulSoup


def extract_remedy(html: str) -> str | None:
    """Return remedy text from recall HTML."""
    soup = BeautifulSoup(html, "html.parser")

    heading = soup.find(
        lambda t: t.name in {"h1", "h2", "h3", "h4"}
        and "remedy" in t.get_text(strip=True).lower()
    )
    if heading:
        p = heading.find_next("p")
        if p:
            text = p.get_text(strip=True)
            if text:
                return text

    strong = soup.find(
        lambda t: t.name in {"b", "strong"}
        and "remedy" in t.get_text(strip=True).lower()
    )
    if strong:
        text = strong.parent.get_text(strip=True)
        if text:
            return text.replace(strong.get_text(strip=True), "").strip()

    return None
