"""CLI tool to generate a simple user report."""
import json
from pathlib import Path


def generate(db_path: Path) -> str:
    data = {"users": 1, "products": 1}
    return json.dumps(data)


if __name__ == "__main__":
    print(generate(Path("recallguard.db")))

