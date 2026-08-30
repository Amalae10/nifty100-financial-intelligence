import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

companies = ["ABB", "INFY", "TCS"]

for company in companies:
    print("\n", company)

    pl = pd.read_sql("""
    SELECT year, sales, net_profit
    FROM profitandloss
    WHERE company_id = ?
    """, conn, params=[company])

    bs = pd.read_sql("""
    SELECT year, equity_capital, reserves
    FROM balancesheet
    WHERE company_id = ?
    """, conn, params=[company])

    df = pl.merge(bs, on="year")

    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d{2,4})$")[0],
        errors="coerce"
    )

    df.loc[df["year_num"] < 100, "year_num"] += 2000
    df = df[df["year"].str.upper() != "TTM"]
    df = df.sort_values("year_num")

    latest = df.iloc[-1]
    start = df.iloc[-6]

    roe = latest["net_profit"] / (
        latest["equity_capital"] + latest["reserves"]
    ) * 100

    revenue_cagr = (
        (latest["sales"] / start["sales"]) ** (1 / 5) - 1
    ) * 100

    print("Year:", latest["year"])
    print("Manual ROE:", round(roe, 6))
    print("Manual Revenue CAGR:", round(revenue_cagr, 6))

conn.close()