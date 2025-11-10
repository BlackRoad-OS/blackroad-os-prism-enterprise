"""Tests for ``parse_numeric_prefix``.

These checks cover both successful numeric parsing and the fallback to 1.0
for invalid prefixes.
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
