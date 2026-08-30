import pandas as pd
import pytest

from src.etl.loader import load_csv

def test_load_csv(tmp_path):
    file = tmp_path / "test.csv"

    pd.DataFrame({"company": ["TCS", "INFY"]}).to_csv(file, index=False)

    result = load_csv(file)

    assert isinstance(result, pd.DataFrame)


def test_row_count(tmp_path):
    file = tmp_path / "test.csv"

    pd.DataFrame({
        "company": ["TCS", "INFY", "RELIANCE"]
    }).to_csv(file, index=False)

    assert len(load_csv(file)) == 3


def test_column_count(tmp_path):
    file = tmp_path / "test.csv"

    pd.DataFrame({
        "company": ["TCS"],
        "year": [2024],
        "sales": [1000]
    }).to_csv(file, index=False)

    assert len(load_csv(file).columns) == 3


def test_column_names(tmp_path):
    file = tmp_path / "test.csv"

    pd.DataFrame({
        "company": ["TCS"],
        "year": [2024]
    }).to_csv(file, index=False)

    result = load_csv(file)

    assert "company" in result.columns
    assert "year" in result.columns


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv("does_not_exist.csv")

