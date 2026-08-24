import pytest

from src.etl.normaliser import (
    normalize_year,
    normalize_ticker,
)


# ============================================================
# normalize_year() — 15 tests
# ============================================================

@pytest.mark.parametrize(
    "input_value, expected",
    [
        (2024, 2024),
        (2023, 2023),
        (2022, 2022),
        ("2024", 2024),
        ("2023", 2023),
        ("FY2024", 2024),
        ("FY 2024", 2024),
        ("FY2023", 2023),
        ("FY 2022", 2022),
        ("2023-24", 2023),
        ("2022-23", 2022),
        ("FY 2023-24", 2023),
        ("FY2021-22", 2021),
        (None, None),
        ("hello", None),
    ],
)
def test_normalize_year(input_value, expected):
    assert normalize_year(input_value) == expected


# ============================================================
# normalize_ticker() — 15 tests
# ============================================================

@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("TCS", "TCS"),
        ("tcs", "TCS"),
        ("Tcs", "TCS"),
        ("TCS.NS", "TCS"),
        ("tcs.ns", "TCS"),
        ("Tcs.Ns", "TCS"),
        ("TCS.BO", "TCS"),
        ("tcs.bo", "TCS"),
        ("Tcs.Bo", "TCS"),
        (" RELIANCE ", "RELIANCE"),
        ("reliance", "RELIANCE"),
        ("reliance.ns", "RELIANCE"),
        ("INFY.NS", "INFY"),
        ("HDFCBANK.NS", "HDFCBANK"),
        (None, None),
    ],
)
def test_normalize_ticker(input_value, expected):
    assert normalize_ticker(input_value) == expected