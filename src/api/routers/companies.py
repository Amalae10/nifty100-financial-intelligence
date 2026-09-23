import sqlite3

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import APIRouter, Query,HTTPException

router = APIRouter()
DB="nifty100.db"

# -------------------------------------------
# Endpoint 1
# ---------------------------------------------
@router.get("/companies")
def get_companies(
    sector:str | None = None,
    market_cap_category:str | None=None,
    search:str | None=Query(default=None)
):
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    query="""
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            c.roe_percentage AS roe_pct,
            c.roce_percentage AS roce_pct
        FROM companies c
        LEFT JOIN sectors s
            ON c.id=s.company_id

        WHERE 1=1
    """
    params=[]

    if sector:
        query += "AND s.broad_sector=?"
        params.append(sector)

    if market_cap_category:
        query += "AND s.market_cap_category =?"
        params.append(market_cap_category)

    if search:
        query += """
            AND (
                LOWER(c.company_name) LIKE ?
                OR LOWER(c.id) LIKE ?
            )
        """
        value=f"%{search.lower()}%"
        params.extend([value,value])

    query += " ORDER BY c.company_name"
    rows=conn.execute(query,params).fetchall()
    conn.close()

    return [dict(row) for row in rows]

# ---------------------------------------------------
#                Endpoint 2
# ---------------------------------------------------

@router.get("/companies/{ticker}")
def get_company(ticker:str):
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    company=conn.execute("""
        SELECT c.*,s.broad_sector,s.sub_sector,
               s.index_weight_pct, s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s ON c.id=s.company_id
        WHERE UPPER(c.id)=UPPER(?)
    """,(ticker,)).fetchone()

    if not company:
        conn.close()
        raise HTTPException(status_code=404,detail="Company not found")

    kpi=conn.execute("""
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
            AND year NOT LIKE '%TTM%'
        ORDER BY CAST(SUBSTR(year,-4) AS INTEGER) DESC
        LIMIT 1
    """,(company["id"],)).fetchone()
    conn.close()

    result=dict(company)
    result["latest_kpis"]=dict(kpi) if kpi else None

    return result

# ---------------------------------------------------
# Endpoint 3 - Profit & Loss
# ---------------------------------------------------

@router.get("/companies/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        "SELECT 1 FROM companies WHERE UPPER(id)=UPPER(?)",
        (ticker,)
    ).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(404, "Company not found")

    query = """
        SELECT *
        FROM profitandloss
        WHERE UPPER(company_id)=UPPER(?)
          AND year != 'TTM'
    """
    params = [ticker]

    if from_year:
        query += " AND CAST(SUBSTR(year,-4) AS INTEGER) >= ?"
        params.append(int(from_year[:4]))

    if to_year:
        query += " AND CAST(SUBSTR(year,-4) AS INTEGER) <= ?"
        params.append(int(to_year[:4]))

    query += " ORDER BY CAST(SUBSTR(year,-4) AS INTEGER)"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]

# ---------------------------------------------------
# Endpoint 4 - Balance Sheet
# ---------------------------------------------------

@router.get("/companies/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        "SELECT 1 FROM companies WHERE UPPER(id)=UPPER(?)",
        (ticker,)
    ).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(404, "Company not found")

    query = """
        SELECT *
        FROM balancesheet
        WHERE UPPER(company_id)=UPPER(?)
          AND year != 'TTM'
    """

    params = [ticker]

    if from_year:
        query += """
            AND date(
                SUBSTR(year,-4) || '-' ||
                CASE SUBSTR(year,1,3)
                    WHEN 'Mar' THEN '03'
                    WHEN 'Sep' THEN '09'
                END || '-01'
            ) >= date(? || '-01')
        """
        params.append(from_year)

    if to_year:
        query += """
            AND date(
                SUBSTR(year,-4) || '-' ||
                CASE SUBSTR(year,1,3)
                    WHEN 'Mar' THEN '03'
                    WHEN 'Sep' THEN '09'
                END || '-01'
            ) <= date(? || '-01')
        """
        params.append(to_year)

    query += " ORDER BY CAST(SUBSTR(year,-4) AS INTEGER), year"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]

# ---------------------------------------------------
# Endpoint 5 - Cash Flow
# ---------------------------------------------------

@router.get("/companies/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        "SELECT 1 FROM companies WHERE UPPER(id)=UPPER(?)",
        (ticker,)
    ).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(404, "Company not found")

    query = """
        SELECT *
        FROM cashflow
        WHERE UPPER(company_id)=UPPER(?)
          AND year != 'TTM'
    """
    params = [ticker]

    if from_year:
        query += " AND CAST(SUBSTR(year,-4) AS INTEGER) >= ?"
        params.append(int(from_year[:4]))

    if to_year:
        query += " AND CAST(SUBSTR(year,-4) AS INTEGER) <= ?"
        params.append(int(to_year[:4]))

    query += " ORDER BY CAST(SUBSTR(year,-4) AS INTEGER)"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]

# ----------------------------------------------------
# Endpoint 6 - Financial Ratios
# ----------------------------------------------------

@router.get("/companies/{ticker}/ratios")
def get_ratios(
    ticker:str,
    year:str | None=None
):
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    exists=conn.execute(
        "SELECT 1 FROM companies WHERE UPPER(id)=UPPER(?)",
        (ticker,)
    ).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(404,"Company not found")

    Query="""
        SELECT *
        FROM financial_ratios
        WHERE UPPER(company_id)=UPPER(?)
    """
    params=[ticker]

    if year:
        Query += "AND year = ?"
        params.append(year)

    Query += """
        ORDER BY
        CASE WHEN year ='TTM' THEN 1 ELSE 0 END,
        CAST(SUBSTR(year,-4) AS INTEGER)
    """

    rows=conn.execute(Query,params).fetchall()
    conn.close()

    return[dict(row) for row in rows]

# ---------------------------------------------------
# Endpoint 7 -Company Tearsheet
# ---------------------------------------------------

@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet(ticker:str):
    ticker=ticker.upper()
    conn=sqlite3.connect(DB)
    exists=conn.execute(
        "SELECT 1 FROM companies WHERE UPPER(id)=?",
        (ticker,)
    ).fetchone()

    conn.close()

    if not exists:
        raise HTTPException(404,"Company not found")

    file_path=Path("reports/tearsheets")/f"{ticker}_tearsheet.pdf"

    if not file_path.exists():
        raise HTTPException(404,"Company not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{ticker}_tearsheet.pdf"
    )