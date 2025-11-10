"""Utility functions for the BlackRoad Prism console."""

from __future__ import annotations

import ast


def parse_numeric_prefix(text: str) -> float:
    """Return the leading numeric value in ``text`` or ``1.0`` if parsing fails.

    The prefix may include negatives or decimals. The function uses
    :func:`ast.literal_eval` for safety instead of ``eval`` and evaluates the
    substring before the first comma. Only ``ValueError`` and ``SyntaxError``
    are suppressed. This covers empty strings, whitespace, non-numeric tokens,
    or malformed expressions, and the default ``1.0`` is returned in those
    cases.
    """
    try:
        # Evaluate only the portion before the first comma to ignore any
        # trailing text (for example, "2, rest"). ``ast.literal_eval`` is
        # intentionally used instead of ``eval`` because it restricts the
        # permitted syntax to Python literals, preventing arbitrary code
        # execution while still accepting ints, floats, and their negative
        # forms.
        value = ast.literal_eval(text.split(",", maxsplit=1)[0].strip())
        if isinstance(value, (int, float)):
            return float(value)
    except (ValueError, SyntaxError):
        # Non-numeric literals—such as strings, malformed expressions, or
        # whitespace—raise ``ValueError``/``SyntaxError`` and fall through to the
        # default of ``1.0``.
        pass
    return 1.0
