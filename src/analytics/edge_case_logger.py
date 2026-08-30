import sqlite3
import pandas as pd

DB = "nifty100.db"
OUT = "output/ratio_edge_cases.log"

with sqlite3.connect(DB) as conn:
    df = pd.read_sql("SELECT * FROM financial_ratios", conn)

logs = []

# CAGR edge cases
cagr_flags = [
    c for c in df.columns
    if c.endswith("_flag") and "cagr" in c
]

for col in cagr_flags:
    bad = df[
        df[col].isin([
            "TURNAROUND",
            "DECLINE_TO_LOSS",
            "BOTH_NEGATIVE",
            "ZERO_BASE"
        ])
    ]

    for _, r in bad.iterrows():
        logs.append(
            f"CAGR | {r.company_id} | {r.year} | "
            f"{col}={r[col]}"
        )

# Debt-free ICR substitution
if "debt_free_flag" in df.columns:
    for _, r in df[df["debt_free_flag"] == "Debt Free"].iterrows():
        logs.append(
            f"DEBT_FREE | {r.company_id} | {r.year} | ICR=N/A"
        )

# Division-by-zero / unavailable ratios
check_cols = [
    "net_profit_margin_pct",
    "return_on_equity_pct",
    "return_on_assets_pct",
    "interest_coverage"
]

for col in check_cols:
    if col in df.columns:
        for _, r in df[df[col].isna()].iterrows():
            logs.append(
                f"NULL_RATIO | {r.company_id} | {r.year} | {col}"
            )

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(logs))

print("ratio_edge_cases.log updated")
print("Logged cases:", len(logs))