import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB = "nifty100.db"


@router.get("/screener")
def screener(
    min_roe: float | None = None,
    max_de: float | None = None,
    min_fcf: float | None = None,
    sector: str | None = None,
    min_rev_cagr_5yr: float | None = None,
    min_pat_cagr_5yr: float | None = None,
    max_pe: float | None = None
):
    # Basic parameter validation
    if min_roe is not None and min_roe < 0:
        raise HTTPException(400, "min_roe cannot be negative")

    if max_de is not None and max_de < 0:
        raise HTTPException(400, "max_de cannot be negative")

    if max_pe is not None and max_pe < 0:
        raise HTTPException(400, "max_pe cannot be negative")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT
            c.id AS ticker,
            c.company_name,
            s.broad_sector AS sector,
            r.return_on_equity_pct AS roe,
            r.debt_to_equity AS de,
            r.free_cash_flow_cr AS fcf,
            r.revenue_cagr_5yr,
            r.pat_cagr_5yr,
            r.pe_ratio,
            r.composite_quality_score
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios r
            ON c.id = r.company_id
        WHERE r.year = 'Mar 2024'
    """

    params = []

    if min_roe is not None:
        query += " AND r.return_on_equity_pct >= ?"
        params.append(min_roe)

    if max_de is not None:
        query += " AND r.debt_to_equity <= ?"
        params.append(max_de)

    if min_fcf is not None:
        query += " AND r.free_cash_flow_cr >= ?"
        params.append(min_fcf)

    if sector:
        query += " AND LOWER(s.broad_sector) = LOWER(?)"
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        query += " AND r.revenue_cagr_5yr >= ?"
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        query += " AND r.pat_cagr_5yr >= ?"
        params.append(min_pat_cagr_5yr)

    if max_pe is not None:
        query += " AND r.pe_ratio <= ?"
        params.append(max_pe)

    query += """
        ORDER BY r.composite_quality_score DESC,
                 c.company_name
    """

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]