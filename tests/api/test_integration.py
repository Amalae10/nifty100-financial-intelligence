import sqlite3
import pandas as pd
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_screener_matches_database():
    response = client.get("/api/v1/screener?min_roe=15")
    assert response.status_code == 200

    api_data = response.json()

    with sqlite3.connect("nifty100.db") as conn:
        dashboard_data = pd.read_sql("""
            SELECT fr.company_id
            FROM financial_ratios fr
            WHERE fr.year = 'Mar 2024'
              AND fr.return_on_equity_pct >= 15
        """, conn)

    api_tickers = {row["ticker"] for row in api_data}
    dashboard_tickers = set(dashboard_data["company_id"])

    assert api_tickers == dashboard_tickers