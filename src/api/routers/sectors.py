import sqlite3
from statistics import median
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB = "nifty100.db"

router = APIRouter()
DB = "nifty100.db"

# ----------------------------------------------
# ENDPOINT 9- Sectors
# ----------------------------------------------

@router.get("/sectors")
def get_sectors():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    sectors = conn.execute("""
        SELECT DISTINCT broad_sector
        FROM sectors
        ORDER BY broad_sector
    """).fetchall()

    result = []

    for sector in sectors:
        name = sector["broad_sector"]

        rows = conn.execute("""
            SELECT
                s.company_id,
                r.return_on_equity_pct AS roe,
                r.pe_ratio AS pe,
                r.debt_to_equity AS de
            FROM sectors s
            LEFT JOIN financial_ratios r
                ON s.company_id = r.company_id
               AND r.year = 'Mar 2024'
            WHERE s.broad_sector = ?
        """, (name,)).fetchall()

        roe = [r["roe"] for r in rows if r["roe"] is not None]
        pe = [r["pe"] for r in rows if r["pe"] is not None]
        de = [r["de"] for r in rows if r["de"] is not None]

        result.append({
            "sector_name": name,
            "company_count": len(rows),
            "median_roe": round(median(roe), 2) if roe else None,
            "median_pe": round(median(pe), 2) if pe else None,
            "median_de": round(median(de), 2) if de else None
        })

    conn.close()
    return result

# ----------------------------------------------
# ENDPOINT 10 - Sector Companies
# ----------------------------------------------

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector:str):
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    exists=conn.execute("""
        SELECT 1
        FROM sectors
        WHERE LOWER(broad_sector)=LOWER(?)
        LIMIT 1
    """,(sector,)).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Sector not found"
        )
    rows=conn.execute("""
        SELECT
            c.id AS ticker,
            c.company_name,
            s.broad_sector AS sector,
            r.return_on_equity_pct AS roe,
            r.return_on_capital_pct AS roce,
            r.net_profit_margin_pct AS npm,
            r.operating_profit_margin_pct AS opm,
            r.debt_to_equity AS de,
            r.revenue_cagr_5yr,
            r.pat_cagr_5yr,
            r.pe_ratio
        FROM companies c
        JOIN sectors s
            ON c.id=s.company_id
        LEFT JOIN financial_ratios r
            ON c.id=r.company_id
            AND r.year='Mar 2024'
        WHERE LOWEr(s.broad_sector)=LOWER(?)
        ORDER BY  c.company_name
    """,(sector,)).fetchall()

    conn.close()
    return[dict(row) for row in rows]