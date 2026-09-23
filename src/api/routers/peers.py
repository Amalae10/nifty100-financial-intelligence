import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB = "nifty100.db"

# -----------------------------------------------
# Endpoint 11 - Peer Group
# -----------------------------------------------
@router.get("/peers/{group_name}")
def get_peers(group_name: str):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    exists = conn.execute("""
        SELECT 1
        FROM peer_groups
        WHERE LOWER(peer_group_name) = LOWER(?)
        LIMIT 1
    """, (group_name,)).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Peer group not found"
        )

    rows = conn.execute("""
        SELECT
            p.company_id AS ticker,
            c.company_name,
            p.metric,
            p.value,
            p.percentile_rank,
            p.year
        FROM peer_percentiles p
        JOIN companies c
            ON p.company_id = c.id
        WHERE LOWER(p.peer_group_name) = LOWER(?)
          AND p.year = 'Mar 2024'
        ORDER BY p.company_id, p.metric
    """, (group_name,)).fetchall()

    conn.close()

    companies = {}

    for row in rows:
        ticker = row["ticker"]

        if ticker not in companies:
            companies[ticker] = {
                "ticker": ticker,
                "company_name": row["company_name"],
                "year": row["year"],
                "metrics": {}
            }

        companies[ticker]["metrics"][row["metric"]] = {
            "value": row["value"],
            "percentile_rank": row["percentile_rank"]
        }

    return list(companies.values())

# -----------------------------------------------
# Endpoint 12 - Company Peer Compare
# -----------------------------------------------

RADAR_METRICS = [
    "roe",
    "roce",
    "net_profit_margin",
    "debt_to_equity",
    "interest_coverage",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow"
]


@router.get("/companies/{ticker}/peers/compare")
def compare_peers(ticker: str):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Find company's peer group
    group = conn.execute("""
        SELECT peer_group_name
        FROM peer_groups
        WHERE UPPER(company_id) = UPPER(?)
        LIMIT 1
    """, (ticker,)).fetchone()

    if not group:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company peer group not found"
        )

    group_name = group["peer_group_name"]

    # Find benchmark
    benchmark = conn.execute("""
        SELECT company_id
        FROM peer_groups
        WHERE peer_group_name = ?
          AND is_benchmark = 1
        LIMIT 1
    """, (group_name,)).fetchone()

    benchmark_ticker = benchmark["company_id"] if benchmark else None

    result = {
        "ticker": ticker.upper(),
        "peer_group": group_name,
        "benchmark": benchmark_ticker,
        "year": "Mar 2024",
        "metrics": {}
    }

    for metric in RADAR_METRICS:

        company = conn.execute("""
            SELECT value, percentile_rank
            FROM peer_percentiles
            WHERE UPPER(company_id) = UPPER(?)
              AND metric = ?
              AND year = 'Mar 2024'
        """, (ticker, metric)).fetchone()

        peer_avg = conn.execute("""
            SELECT AVG(value)
            FROM peer_percentiles
            WHERE peer_group_name = ?
              AND metric = ?
              AND year = 'Mar 2024'
        """, (group_name, metric)).fetchone()[0]

        benchmark_value = conn.execute("""
            SELECT value
            FROM peer_percentiles
            WHERE company_id = ?
              AND metric = ?
              AND year = 'Mar 2024'
        """, (benchmark_ticker, metric)).fetchone()

        result["metrics"][metric] = {
            "company_value": company["value"] if company else None,
            "company_percentile": company["percentile_rank"] if company else None,
            "peer_average": peer_avg,
            "benchmark_value": (
                benchmark_value["value"]
                if benchmark_value else None
            )
        }

    conn.close()
    return result