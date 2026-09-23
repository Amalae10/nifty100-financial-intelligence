import sqlite3
from fastapi import APIRouter,HTTPException

router = APIRouter()
DB="nifty100.db"

# -----------------------------------------------
# Endpoint 15 - Company Documents
# -----------------------------------------------

@router.get("/companies/{ticker}/documents")
def get_documents(
    ticker:str,
    from_year:int =2019,
    to_year:int=2024
):
    if from_year > to_year:
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year"
        )

    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    company=conn.execute("""
        SELECT  id
        FROM companies
        WHERE UPPER(id)=UPPER(?)
    """,(ticker,)).fetchone()

    if not company:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    rows=conn.execute("""
        SELECT
            year,annual_report
        FROM documents
        WHERE company_id=?
            AND CAST(year AS INTEGER) BETWEEN ? AND ?
        ORDER BY CAST(year AS INTEGER) DESC
    """,(
        company["id"],
        from_year,
        to_year
    )).fetchall()

    conn.close()

    return [
        {
            "year":row["year"],
            "annual_report":row["annual_report"],
            "is_url_valid":bool(
                row["annual_report"]
                and row["annual_report"].startswith(
                    ("http://","https://")
                )
            )
        }
        for row in rows
    ]