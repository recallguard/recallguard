"""Match user items against known recalls."""
from typing import List, Dict


def check_user_items(user_items: List[str], recalls: List[Dict]) -> List[str]:

    """Return user items that appear in the recall list.

    Matching is case-insensitive to handle variations in product names.
    """
    recalled_products = {recall.get("product", "").lower() for recall in recalls}
    return [item for item in user_items if item.lower() in recalled_products]

    """Return user items that appear in the recall list."""
    recalled_products = {recall.get("product") for recall in recalls}
    return [item for item in user_items if item in recalled_products]


