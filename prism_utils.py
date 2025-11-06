"""Utility helpers for Prism console scripts."""

from __future__ import annotations

import re

# Match an optional sign and decimal number at the start of the string.
#
# The pattern also accepts numbers like ``.5`` or ``-.25`` that omit the
# leading ``0`` before the decimal point. The negative lookahead ensures the
# match is not immediately followed by an alphanumeric character so that
# strings such as ``"1a"`` are treated as invalid.
_NUMERIC_PREFIX = re.compile(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?![0-9A-Za-z_])")


def parse_numeric_prefix(text: str) -> float:
    """Extract a leading decimal value from ``text``.

    Numbers lacking a leading zero (``".5"``) or containing a sign are
    accepted, while invalid prefixes (``"1a"``) fall back to ``1.0``.
    Trailing characters after the numeric component are ignored.
    """

    match = _NUMERIC_PREFIX.match(text)
    if not match:
        return 1.0
    try:
        return float(match.group(1))
    except ValueError:  # pragma: no cover - defensive guard
        return 1.0


__all__ = ["parse_numeric_prefix"]

