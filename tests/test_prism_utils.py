"""Tests for ``parse_numeric_prefix``.

The cases below capture both valid numeric prefixes and the fallback behavior
when the input does not start with a parseable number.
"""

from prism_utils import parse_numeric_prefix


def test_parse_numeric_prefix_valid():
    """Return the numeric prefix when the input starts with a valid number."""
    assert parse_numeric_prefix("2, rest") == 2.0
    assert parse_numeric_prefix("3.5") == 3.5


def test_parse_numeric_prefix_invalid():
    """Default to 1.0 when the prefix is missing or cannot be parsed."""
    assert parse_numeric_prefix("abc") == 1.0
    assert parse_numeric_prefix("1a") == 1.0
