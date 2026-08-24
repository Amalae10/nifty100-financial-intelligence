from src.etl.loader import load_csv, get_connection
import pandas as pd

conn = get_connection()
audit = []

# Companies
companies = load_csv("data/raw/Companies.csv")
read = len(companies)

companies["id"] = companies["id"].str.strip().str.upper()
companies.to_sql("companies", conn, if_exists="append", index=False)

audit.append(["companies", read, len(companies), read - len(companies), 0])


def clean(df):
    df["company_id"] = df["company_id"].astype(str).str.strip().str.upper()
    df = df[df["company_id"].isin(companies["id"])]
    return df.drop_duplicates(["company_id", "year"], keep="last")


# Core tables
core = {
    "profitandloss": "Profit & Loss.csv",
    "balancesheet": "Balance Sheet.csv",
    "cashflow": "Cash Flow.csv",
}

for table, file in core.items():
    raw = load_csv(f"data/raw/{file}")
    read = len(raw)

    df = clean(raw)
    df.to_sql(table, conn, if_exists="append", index=False)

    audit.append([table, read, len(df), read - len(df), 0])
    print(table, len(df))


# Other tables
extra = {
    "sectors": "sectors.csv",
    "peer_groups": "peer_groups.csv",
    "financial_ratios": "financial_ratios.csv",
    "market_cap": "market_cap.csv",
    "stock_prices": "stock_prices.csv",
    "analysis": "Analysis.csv",
    "documents": "Documents.csv",
    "prosandcons": "Pros & Cons.csv",
}

for table, file in extra.items():
    df = load_csv(f"data/raw/{file}")
    read = len(df)

    if table == "documents":
        df = df.rename(columns={
            "Year": "year",
            "Annual_Report": "annual_report"
        })

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].astype(str).str.strip().str.upper()
        df = df[df["company_id"].isin(companies["id"])]

    df.to_sql(table, conn, if_exists="append", index=False)

    audit.append([table, read, len(df), read - len(df), 0])
    print(table, len(df))


# Save audit
pd.DataFrame(
    audit,
    columns=[
        "table",
        "rows_read",
        "rows_loaded",
        "rows_rejected",
        "critical_rejections"
    ]
).to_csv("output/load_audit.csv", index=False)

conn.commit()
conn.close()

print("Full data load completed")