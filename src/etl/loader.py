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