import sqlite3
import pandas as pd

DB = "nifty100.db"

with sqlite3.connect(DB) as conn:
    df = pd.read_sql("""
    SELECT
        fr.company_id,
        fr.year,
        fr.return_on_capital_pct,
        s.broad_sector,
        c.roce_percentage AS source_roce
    FROM financial_ratios fr
    JOIN sectors s
      ON fr.company_id = s.company_id
    JOIN companies c
      ON fr.company_id = c.id
    """, conn)

# Extract fiscal year
df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{4})$")[0],
    errors="coerce"
)

# Keep latest fiscal year for each company
latest = (
    df.sort_values("year_num")
    .groupby("company_id")
    .tail(1)
    .copy()
)

# Financial-sector companies only
financials = latest[
    latest["broad_sector"] == "Financials"
].copy()

# Latest-year sector median
financials["sector_roce_median"] = (
    financials["return_on_capital_pct"].median()
)

financials["roce_difference"] = (
    financials["return_on_capital_pct"]
    - financials["sector_roce_median"]
)

financials["sector_roce_status"] = financials["roce_difference"].apply(
    lambda x: (
        "Above Sector"
        if pd.notna(x) and x > 0
        else "Below Sector"
        if pd.notna(x)
        else "Insufficient Data"
    )
)

financials["source_difference"] = (
    financials["return_on_capital_pct"]
    - financials["source_roce"]
)

financials["source_anomaly"] = financials["source_difference"].apply(
    lambda x: (
        "CHECK"
        if pd.notna(x) and abs(x) > 5
        else "OK"
    )
)

financials["note"] = financials["source_anomaly"].map({
    "CHECK": "ROCE differs from source by more than 5 percentage points",
    "OK": "Within tolerance"
})

financials.to_csv(
    "output/sector_roce_notes.csv",
    index=False
)

print("sector_roce_notes.csv updated")
print("Rows:", len(financials))
print(
    "Anomalies:",
    (financials["source_anomaly"] == "CHECK").sum()
)