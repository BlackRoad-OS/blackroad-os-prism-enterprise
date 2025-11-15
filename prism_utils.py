"""Miscellaneous helpers used across Prism Console."""

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
    """Return the leading numeric value in ``text`` or ``1.0`` if parsing fails."""
# Regex for a decimal number, allowing leading whitespace, optional sign and fraction.
_NUMERIC_PREFIX = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)")


def parse_numeric_prefix(text: str) -> float:
    """Extracts the leading decimal value from ``text``.

    match = _NUMERIC_PREFIX.match(text)
    if not match:
        return 1.0
    try:
        return float(match.group(1))
    except ValueError:  # pragma: no cover - defensive guard
        return 1.0


__all__ = ["parse_numeric_prefix"]
