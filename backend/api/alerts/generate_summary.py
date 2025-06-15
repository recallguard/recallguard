"""Generate AI-based summaries for recalls."""


def generate_summary(recall: dict) -> str:
    """Return a human-friendly summary of a recall."""
    title = recall.get("title", "Recall")
    product = recall.get("product", "product")
    return f"{title} involving {product}."

