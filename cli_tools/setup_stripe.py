"""Create Stripe products and prices for RecallHero."""
"""Create Stripe products and prices for RecallHero."""
import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCTS = {
    "pro": {
        "name": "RecallHero Pro",
        "prices": [
            {
                "lookup_key": "pro-monthly",
                "unit_amount": 900,
                "recurring": {"interval": "month"},
            }
        ],
    },
    "enterprise-seat": {
        "name": "RecallHero Enterprise Seat",
        "prices": [
            {
                "lookup_key": "enterprise-seat",
                "unit_amount": 1500,
                "recurring": {"interval": "month"},
            }
        ],
    },
    "enterprise-api": {
        "name": "RecallHero Enterprise API Usage",
        "prices": [
            {
                "lookup_key": "enterprise-api",
                "unit_amount": 1,
                "currency": "usd",
                "recurring": {"interval": "month", "usage_type": "metered"},
                "transform_usage": {"divide_by": 100, "round": "up"},
            }
        ],
    },
}


def main() -> None:
    for pid, cfg in PRODUCTS.items():
        product = stripe.Product.create(name=cfg["name"], id=pid)
        for price in cfg["prices"]:
            stripe.Price.create(product=product.id, **price, currency="usd")
        print(f"Created {product.name}")


if __name__ == "__main__":
    main()
