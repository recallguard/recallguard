"""Simple task scheduler using schedule library."""
import schedule
import time
from typing import Callable


def every_minute(func: Callable) -> None:
    schedule.every(1).minutes.do(func)


def run_forever() -> None:
    while True:
        schedule.run_pending()
        time.sleep(1)

