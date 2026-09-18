import re
import sqlite3
from pathlib import Path

import pandas as pd

DB = "nifty100.db"
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%", re.I)


def parse_analysis():
    with sqlite3.connect(DB) as conn:
        analysis = pd.read_sql("SELECT * FROM analysis", conn)
        ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)

    parsed = []
    failures = []
    reviews = []

    for _, row in analysis.iterrows():
        for field in FIELDS:
            text = str(row[field]).strip()
            match = PATTERN.search(text)

            if not match:
                failures.append({
                    "company_id": row["company_id"],
                    "metric_type": field,
                    "raw_text": text
                })
                continue

            period = int(match.group(1))
            value = float(match.group(2))

            parsed.append({
                "company_id": row["company_id"],
                "metric_type": field,
                "period_years": period,
                "value_pct": value
            })

            # Cross-validation for Sales and Profit CAGR
            if field == "compounded_sales_growth":
                ratio_col = f"revenue_cagr_{period}yr"

            elif field == "compounded_profit_growth":
                ratio_col = f"pat_cagr_{period}yr"

            else:
                continue

            if ratio_col not in ratios.columns:
                continue

            company_rows = ratios[
                ratios["company_id"] == row["company_id"]
            ]

            values = pd.to_numeric(
                company_rows[ratio_col],
                errors="coerce"
            ).dropna()

            if values.empty:
                continue

            computed = float(values.iloc[-1])
            divergence = abs(value - computed)

            if divergence > 5:
                reviews.append({
                    "company_id": row["company_id"],
                    "metric_type": field,
                    "period_years": period,
                    "parsed_value_pct": value,
                    "computed_value_pct": round(computed, 2),
                    "divergence_pct": round(divergence, 2),
                    "manual_review": "YES"
                })

    parsed_df = pd.DataFrame(parsed)
    failures_df = pd.DataFrame(failures)
    reviews_df = pd.DataFrame(reviews)

    parsed_df.to_csv(
        OUTPUT / "analysis_parsed.csv",
        index=False
    )

    failures_df.to_csv(
        OUTPUT / "parse_failures.csv",
        index=False
    )

    reviews_df.to_csv(
        OUTPUT / "cross_validation.csv",
        index=False
    )

    print("Parsed rows:", len(parsed_df))
    print("Parse failures:", len(failures_df))
    print("CAGR divergences > 5%:", len(reviews_df))

    print("\nCreated:")
    print("output/analysis_parsed.csv")
    print("output/parse_failures.csv")
    print("output/cross_validation.csv")


if __name__ == "__main__":
    parse_analysis()
