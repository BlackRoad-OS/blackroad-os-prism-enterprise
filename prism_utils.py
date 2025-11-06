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
# Matches optional leading whitespace, an optional sign, digits, and an optional
# fractional part.
_NUMERIC_PREFIX = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)")


def parse_numeric_prefix(text: str) -> float:
    """Extract a leading decimal value from ``text``.

    Numbers lacking a leading zero (``".5"``) or containing a sign are
    accepted, while invalid prefixes (``"1a"``) fall back to ``1.0``.
    Trailing characters after the numeric component are ignored.
    """Return the leading numeric value in ``text`` or ``1.0`` if parsing fails.

    The prefix may include negatives or decimals. The function uses
    :func:`ast.literal_eval` for safety instead of ``eval`` and evaluates the
    substring before the first comma. Only ``ValueError`` and ``SyntaxError``
    are suppressed—covering empty strings, whitespace, non-numeric tokens, or
    malformed expressions—and the default ``1.0`` is returned in those cases.
    """

    match = _NUMERIC_PREFIX.match(text)
    if not match:
        return 1.0
    try:
        return float(match.group(1))
    except ValueError:  # pragma: no cover - defensive guard
        return 1.0


__all__ = ["parse_numeric_prefix"]

