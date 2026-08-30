import sqlite3
import pandas as pd

from src.analytics.cashflow_kpis import allocation, cfo_pat_ratio

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT
    c.company_id,
    c.year,
    c.operating_activity AS cfo,
    c.investing_activity AS cfi,
    c.financing_activity AS cff,

    p.net_profit AS pat
FROM cashflow c
LEFT JOIN profitandloss p
ON c.company_id = p.company_id
AND c.year = p.year
""", conn)

rows = []

for _, r in df.iterrows():
    ratio = cfo_pat_ratio(r.cfo, r.pat) if pd.notna(r.pat) else None

    signs, label = allocation(
        r.cfo,
        r.cfi,
        r.cff,
        ratio
    )

    rows.append([
        r.company_id,
        r.year,
        signs[0],
        signs[1],
        signs[2],
        label
    ])

pd.DataFrame(
    rows,
    columns=[
        "company_id",
        "year",
        "cfo_sign",
        "cfi_sign",
        "cff_sign",
        "pattern_label"
    ]
).to_csv(
    "output/capital_allocation.csv",
    index=False
)

conn.close()

print("capital_allocation.csv created:", len(rows))