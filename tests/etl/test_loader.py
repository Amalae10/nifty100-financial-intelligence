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

def test_core_files_defined():
    from src.etl.loader import CORE_FILES
    assert len(CORE_FILES) == 7


def test_companies_is_core_file():
    from src.etl.loader import CORE_FILES
    assert "Companies.csv" in CORE_FILES


def test_get_connection():
    from src.etl.loader import get_connection
    conn = get_connection()
    assert conn is not None
    conn.close()


def test_foreign_keys_enabled():
    from src.etl.loader import get_connection
    conn = get_connection()
    value = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    conn.close()
    assert value == 1


def test_load_to_db(tmp_path, monkeypatch):
    import sqlite3
    import pandas as pd
    import src.etl.loader as loader

    db = tmp_path / "test.db"

    monkeypatch.setattr(
        loader,
        "get_connection",
        lambda: sqlite3.connect(db)
    )

    df = pd.DataFrame({"id": [1], "name": ["TCS"]})
    loader.load_to_db(df, "test_table")

    conn = sqlite3.connect(db)
    count = conn.execute(
        "SELECT COUNT(*) FROM test_table"
    ).fetchone()[0]
    conn.close()

    assert count == 1