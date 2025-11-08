"""CLI helper for running a Lucidia Encompass vote.

Example
-------
$ python scripts/encompass_demo.py --prompt "Should we deploy the patch?"
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from agents.lucidia_encompass import run


def main(argv: Any = None) -> None:
    """Execute the demo CLI."""

    parser = argparse.ArgumentParser(description="Run a Lucidia Encompass vote")
    parser.add_argument("--prompt", required=True, help="Prompt to submit to all personas")
    args = parser.parse_args(argv)

    result = run(args.prompt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
