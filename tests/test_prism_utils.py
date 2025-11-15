"""Tests for ``parse_numeric_prefix``."""
"""Tests for :mod:`prism_utils`."""
import ast

import pytest

from prism_utils import parse_numeric_prefix


def test_parse_numeric_prefix_valid():
    assert parse_numeric_prefix("2, rest") == 2.0
    assert parse_numeric_prefix("3.5") == 3.5
    assert parse_numeric_prefix("-1 stuff") == -1.0
    assert parse_numeric_prefix("+4") == 4.0
    assert parse_numeric_prefix(" 7") == 7.0


def test_parse_numeric_prefix_invalid():
    assert parse_numeric_prefix("abc") == 1.0
    assert parse_numeric_prefix("1a") == 1.0
    assert parse_numeric_prefix("") == 1.0
    assert parse_numeric_prefix("+a") == 1.0
@pytest.mark.parametrize(
    "text, expected",
    [
        ("2, rest", 2.0),
        ("3.5", 3.5),
        ("-4, things", -4.0),
        ("-0.5", -0.5),
    ],
)
def test_parse_numeric_prefix_valid(text: str, expected: float) -> None:
    """Return parsed value for valid numeric prefixes."""
    assert parse_numeric_prefix(text) == expected


@pytest.mark.parametrize("text", ["", "   ", "abc", "1a", "("])
def test_parse_numeric_prefix_invalid(text: str) -> None:
    """Fall back to ``1.0`` when parsing fails."""
    assert parse_numeric_prefix(text) == 1.0


@pytest.mark.parametrize("exc", [RecursionError, MemoryError])
def test_parse_numeric_prefix_other_errors(monkeypatch, exc):
    def bad_eval(_):
        raise exc()

    monkeypatch.setattr(ast, "literal_eval", bad_eval)
    assert parse_numeric_prefix("2") == 1.0
