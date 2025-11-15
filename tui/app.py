"""Placeholder Text UI using Rich."""
from __future__ import annotations

from rich.console import Console


def run() -> None:
    console = Console()
    console.print("TUI not implemented; demo placeholder.")
import json
from pathlib import Path
from typing import Dict


def load_theme(name: str) -> Dict[str, str]:
    path = Path(__file__).resolve().parent / "themes" / f"{name}.json"
    return json.loads(path.read_text())


def run(theme: str = "light") -> Dict[str, str]:
    return load_theme(theme)
