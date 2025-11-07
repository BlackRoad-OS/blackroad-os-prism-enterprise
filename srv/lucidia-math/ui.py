"""User-facing interfaces for the Lucidia math platform."""

from __future__ import annotations

import json
from typing import Callable, Dict

from . import finance, fractals, logic, numbers, primes, proofs, waves
from .api_ambr import app  # FastAPI application exposed for runtime

MENU: Dict[str, Callable[[], object]] = {
    "Logic": lambda: logic.persist_truth_table(
        logic.generate_truth_table(["A", "B"], expression="A and not B")
    ).as_posix(),
    "Primes": lambda: primes.demo(),
    "Proofs": lambda: proofs.demo(),
    "Waves": lambda: waves.demo(),
    "Finance": finance.demo,
    "Numbers": numbers.demo,
    "Fractals": lambda: fractals.demo(),
}


def repl() -> None:
    """Simple command line REPL exposing demo functions."""

    options = list(MENU.keys())
    while True:
        for idx, name in enumerate(options, start=1):
            print(f"{idx}. {name}")
        print("0. Exit")
        try:
            choice = int(input("Select module: "))
        except ValueError:
            print("Invalid input\n")
            continue
        if choice == 0:
            break
        if 1 <= choice <= len(options):
            name = options[choice - 1]
            result = MENU[name]()
            print(json.dumps({"result": result}, indent=2))
        else:
            print("Invalid selection\n")


__all__ = ["repl", "app"]
