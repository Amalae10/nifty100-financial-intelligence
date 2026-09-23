from pathlib import Path
import pandas as pd
import sqlite3

CORE_FILES = {
    "Analysis.csv",
    "Balance Sheet.csv",
    "Cash Flow.csv",
    "Companies.csv",
    "Documents.csv",
    "Profit & Loss.csv",
    "Pros & Cons.csv"
}


def load_csv(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    if file_path.name in CORE_FILES:
        return pd.read_csv(file_path, skiprows=1) #skip rows is used to skip first rows and use as he header.

    return pd.read_csv(file_path)

def get_connection():
    conn = sqlite3.connect("nifty100.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_to_db(df, table):
    conn = get_connection()

    df.to_sql(
        table,
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()
    conn.close()

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