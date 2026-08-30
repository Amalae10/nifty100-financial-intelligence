import sqlite3
import os
import pandas as pd

from src.analytics.ratios import roe,roce

conn=sqlite3.connect("nifty100.db")

financials = pd.read_sql("""
SELECT DISTINCT company_id
FROM sectors
WHERE broad_sector = 'Financials'
""", conn)
print("Financial companies:", len(financials))
print(financials.to_string(index=False))

df=pd.read_sql("""
SELECT
    p.company_id,
    p.year,
    p.net_profit,
    p.operating_profit,
    p.other_income,
    b.equity_capital,
    b.reserves,
    b.borrowings,
    c.roe_percentage AS source_roe,
    c.roce_percentage AS source_roce
FROM profitandloss p
JOIN balancesheet b
    ON p.company_id=b.company_id
    AND p.year = b.year
JOIN companies c
    ON p.company_id=c.id
""",conn)
conn.close()

# calculate ROE and ROCE

df["computed_roe"]=df.apply(
    lambda r:roe(
        r.net_profit,
        r.equity_capital,
        r.reserves
    ),
    axis=1
)

df["computed_roce"]=df.apply(
    lambda r:roce(
        r.operating_profit + r.other_income,
        r.equity_capital,
        r.reserves,
        r.borrowings
    ),
    axis=1
)

df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{2,4})$")[0],
    errors="coerce"
)

df.loc[df["year_num"] < 100, "year_num"] += 2000

df = df.loc[
    df.groupby("company_id")["year_num"].idxmax()
].copy()

df["roe_diff"] = (
    df["computed_roe"] - df["source_roe"]
).abs()

df["roce_diff"] = (
    df["computed_roce"] - df["source_roce"]
).abs()

issues = df[
    (df["roe_diff"] > 5) |
    (df["roce_diff"] > 5)
].copy()

# Find differences greater than 5%

df["roe_diff"]=(
    df["computed_roe"] - df["source_roe"]
).abs()

df["roce_diff"]=(
    df["computed_roce"] - df["source_roce"]
).abs()

issues=df[
    (df["roe_diff"]>5) |
    (df["roce_diff"]>5)
].copy()

# Categorise the anomalies

def category(row):
    if row["roe_diff"] > 50 or row["roce_diff"] > 50:
        return "data source issue"

    if row["roe_diff"] > 5 and row["roce_diff"] > 5:
        return "formula discrepancy"

    return "version difference"

issues["category"]=issues.apply(category,axis=1)

# Create the log

os.makedirs("output",exist_ok=True)

issues[[
    "company_id",
    "year",
    "source_roe",
    "computed_roe",
    "roe_diff",
    "source_roce",
    "computed_roce",
    "roce_diff",
    "category"
]].to_csv("output/ratio_edge_cases.log",
          index=False
)

print("edge cases logged:", len(issues))