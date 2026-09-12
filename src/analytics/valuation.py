import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "nifty100.db"
OUTPUT_DIR = ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def extract_year(value):
    text = str(value)

    year = pd.Series([text]).str.extract(r"(20\d{2})")[0].iloc[0]

    if pd.notna(year):
        return int(year)

    short = pd.Series([text]).str.extract(r"-(\d{2})$")[0].iloc[0]

    if pd.notna(short):
        return 2000 + int(short)

    return None


def load_data():
    with sqlite3.connect(DB_PATH) as conn:

        companies = pd.read_sql("""
            SELECT
                id AS company_id,
                company_name
            FROM companies
        """, conn)

        sectors = pd.read_sql("""
            SELECT
                company_id,
                broad_sector
            FROM sectors
        """, conn)

        market = pd.read_sql("""
            SELECT
                company_id,
                year,
                market_cap_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda
            FROM market_cap
        """, conn)

        ratios = pd.read_sql("""
            SELECT
                company_id,
                year,
                free_cash_flow_cr
            FROM financial_ratios
        """, conn)

    return companies, sectors, market, ratios


def build_valuation():

    companies, sectors, market, ratios = load_data()

    market["year_num"] = market["year"].apply(extract_year)
    ratios["year_num"] = ratios["year"].apply(extract_year)

    for col in [
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda"
    ]:
        market[col] = pd.to_numeric(
            market[col],
            errors="coerce"
        )

    ratios["free_cash_flow_cr"] = pd.to_numeric(
        ratios["free_cash_flow_cr"],
        errors="coerce"
    )

    # Latest year
    latest_year = int(
        market["year_num"].dropna().max()
    )

    latest_market = market[
        market["year_num"] == latest_year
    ].copy()

    latest_ratios = ratios[
        ratios["year_num"] == latest_year
    ].copy()

    # 5-year median P/E
    last_5_years = market[
        market["year_num"] >= latest_year - 4
    ].copy()

    median_5yr = (
        last_5_years
        .groupby("company_id")["pe_ratio"]
        .median()
        .reset_index()
        .rename(
            columns={
                "pe_ratio": "5yr_median_PE"
            }
        )
    )

    # Merge data
    df = (
        latest_market
        .merge(
            latest_ratios[
                ["company_id", "free_cash_flow_cr"]
            ],
            on="company_id",
            how="left"
        )
        .merge(
            companies,
            on="company_id",
            how="left"
        )
        .merge(
            sectors,
            on="company_id",
            how="left"
        )
        .merge(
            median_5yr,
            on="company_id",
            how="left"
        )
    )

    # FCF Yield
    df["FCF_yield_pct"] = (
        df["free_cash_flow_cr"]
        / df["market_cap_crore"]
        * 100
    )

    # Sector Median P/E
    df["sector_median_PE"] = (
        df.groupby("broad_sector")["pe_ratio"]
        .transform("median")
    )

    # P/E vs Sector Median %
    df["PE_vs_sector_median_pct"] = (
        (
            df["pe_ratio"]
            - df["sector_median_PE"]
        )
        / df["sector_median_PE"]
        * 100
    )

    # Valuation Flag
    def valuation_flag(row):

        pe = row["pe_ratio"]
        median = row["sector_median_PE"]

        if pd.isna(pe) or pd.isna(median):
            return "Fair"

        if pe > median * 1.5:
            return "Caution"

        if pe < median * 0.7:
            return "Discount"

        return "Fair"

    df["flag"] = df.apply(
        valuation_flag,
        axis=1
    )

    # Final Excel output
    output = df[[
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag"
    ]].copy()

    output.columns = [
        "company_id",
        "company_name",
        "sector",
        "P/E",
        "P/B",
        "EV/EBITDA",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag"
    ]
    output = output.fillna("N/A")
    output.to_excel(
        OUTPUT_DIR / "valuation_summary.xlsx",
        index=False
    )

    # Caution / Discount only
    flags = df[
        df["flag"].isin(
            ["Caution", "Discount"]
        )
    ][[
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "sector_median_PE",
        "PE_vs_sector_median_pct",
        "FCF_yield_pct",
        "flag"
    ]].copy()

    flags.to_csv(
        OUTPUT_DIR / "valuation_flags.csv",
        index=False
    )

    print("Latest year:", latest_year)
    print("Companies:", len(output))

    print()
    print(output["flag"].value_counts())

    print(
        "\nCreated:",
        OUTPUT_DIR / "valuation_summary.xlsx"
    )

    print(
        "Created:",
        OUTPUT_DIR / "valuation_flags.csv"
    )


if __name__ == "__main__":
    build_valuation()