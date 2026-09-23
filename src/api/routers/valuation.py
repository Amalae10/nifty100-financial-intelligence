import sqlite3
from fastapi import APIRouter,HTTPException

router = APIRouter()
DB="nifty100.db"

# -----------------------------------------------
# Endpoint 13 - Market Cap / Valuation
# -----------------------------------------------
@router.get("/market-cap/{ticker}")
def get_market_cap(
    ticker: str,
    from_year: int = 2019,
    to_year: int = 2024
):
    if from_year > to_year:
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year"
        )

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    company = conn.execute("""
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
    """, (ticker,)).fetchone()

    if not company:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    rows = conn.execute("""
        SELECT
            year,
            market_cap_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct AS div_yield
        FROM market_cap
        WHERE company_id = ?
          AND CAST(year AS INTEGER) BETWEEN ? AND ?
        ORDER BY CAST(year AS INTEGER)
    """, (
        company["id"],
        from_year,
        to_year
    )).fetchall()

    conn.close()

    return [dict(row) for row in rows]