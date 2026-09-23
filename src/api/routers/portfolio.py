import sqlite3
import numpy as np
from fastapi import APIRouter

router = APIRouter()
DB="nifty100.db"

METRICS=[
    "return_on_equity_pct",
    "return_on_capital_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "fcf_cagr_5yr",
    "cfo_pat_ratio"
]

# -----------------------------------------------
# Endpoint 14 - Portfolio Statistics
# -----------------------------------------------

@router.get("/portfolio/stats")
def portfolio_stats(year:str = "Mar 2024"):
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    result=[]
    for metric in METRICS:
        rows =conn.execute(
            f"""
            SELECT {metric}
            FROM financial_ratios
            WHERE year=?
                AND {metric} IS NOT NULL
            """,
            (year,)).fetchall()

        values=[row[metric] for row in rows]

        result.append({
            "metric":metric,
            "P10": round(float(np.percentile(values, 10)), 2),
            "P25": round(float(np.percentile(values, 25)), 2),
            "P50": round(float(np.percentile(values, 50)), 2),
            "P75": round(float(np.percentile(values, 75)), 2),
            "P90": round(float(np.percentile(values, 90)), 2),
            "Mean": round(float(np.mean(values)), 2),
            "Std": round(float(np.std(values)), 2)
        })

    conn.close()
    return result