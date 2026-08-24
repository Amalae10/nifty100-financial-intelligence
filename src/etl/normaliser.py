import re
import pandas as pd


def normalize_year(value):
    """
    Convert different year formats into an integer year.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    match = re.search(r"(19|20)\d{2}", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):
    """
    Standardize stock ticker symbols.
    """

    if pd.isna(value):
        return None

    ticker = str(value).strip().upper()

    ticker = re.sub(r"\.(NS|BO)$", "", ticker)

    return ticker