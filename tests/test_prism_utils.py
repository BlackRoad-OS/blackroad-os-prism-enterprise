from prism_utils import parse_numeric_prefix


def test_parse_numeric_prefix_valid():
    assert parse_numeric_prefix("2, rest") == 2.0
    assert parse_numeric_prefix("3.5") == 3.5
    assert parse_numeric_prefix("2 rest") == 2.0
    assert parse_numeric_prefix(" -4.2 extra") == -4.2
    assert parse_numeric_prefix("2e3") == 2000.0
    assert parse_numeric_prefix("-1.5e-2 extra") == -0.015
    assert parse_numeric_prefix(".5E+3 stuff") == 500.0
    assert parse_numeric_prefix("6.02E23 molecules") == 6.02e23


def test_parse_numeric_prefix_invalid():
    assert parse_numeric_prefix("abc") == 1.0
    assert parse_numeric_prefix("1a") == 1.0
    assert parse_numeric_prefix("7e+") == 1.0
