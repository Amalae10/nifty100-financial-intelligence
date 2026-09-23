import time
import sqlite3

from fastapi import APIRouter,HTTPException

router=APIRouter()

DB="nifty100.db"
START_TIME=time.time()
VERSION="1.0.0"

# 10 core tables for AC-11
TABLES=[
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "sectors",
    "market_cap",
    "stock_prices",
    "documents",
    "analysis"
]

@router.get("/health")
def health():
    try:
        conn=sqlite3.connect(DB)

        counts={
            table:conn.execute(
                f"SELECT COUnt(*) FROM {table}"
            ).fetchone()[0]
            for table in TABLES
        }

        conn.close()

        return {
            "status":"ok",
            "db_row_counts":counts,
            "uptime_seconds":round(time.time()-START_TIME,2),
            "version":VERSION
        }
    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )