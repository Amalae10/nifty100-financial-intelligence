import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB = "nifty100.db"

KPIS = [
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


def main():

    conn = sqlite3.connect(DB)

    df = pd.read_sql(
        "SELECT company_id, year, " + ", ".join(KPIS) +
        " FROM financial_ratios",
        conn
    )

    sectors = pd.read_sql(
        "SELECT company_id, broad_sector FROM sectors",
        conn
    )

    conn.close()

    # Remove TTM and extract year
    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    df = df.dropna(subset=["year_num"])

    # Latest financial year per company
    df = (
        df.sort_values(["company_id", "year_num"])
        .groupby("company_id")
        .tail(1)
    )

    df[KPIS] = df[KPIS].apply(
        pd.to_numeric,
        errors="coerce"
    )

    print("Companies:", len(df))

    # --------------------------------
    # 1. CORRELATION HEATMAP
    # --------------------------------

    correlation = df[KPIS].corr(method="pearson")

    os.makedirs("reports", exist_ok=True)

    plt.figure(figsize=(12, 9))

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0
    )

    plt.title("Nifty 100 KPI Correlation Matrix")
    plt.tight_layout()

    plt.savefig(
        "reports/correlation_heatmap.png",
        dpi=150
    )

    plt.close()

    print("Created: reports/correlation_heatmap.png")

    # --------------------------------
    # 2. Z-SCORE OUTLIER DETECTION
    # --------------------------------

    df = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    outliers = []

    for kpi in KPIS:

        mean = df.groupby(
            "broad_sector"
        )[kpi].transform("mean")

        std = df.groupby(
            "broad_sector"
        )[kpi].transform("std")

        z_score = (df[kpi] - mean) / std

        mask = z_score.abs() > 3

        temp = df.loc[
            mask,
            ["company_id", "broad_sector", kpi]
        ].copy()

        temp["metric"] = kpi
        temp["value"] = temp[kpi]
        temp["z_score"] = z_score[mask].round(2)

        temp = temp[
            [
                "company_id",
                "broad_sector",
                "metric",
                "value",
                "z_score"
            ]
        ]

        outliers.append(temp)

    outlier_report = pd.concat(
        outliers,
        ignore_index=True
    )

    os.makedirs("output", exist_ok=True)

    outlier_report.to_csv(
        "output/outlier_report.csv",
        index=False
    )

    print("Outliers found:", len(outlier_report))
    print("Created: output/outlier_report.csv")

    # --------------------------------
    # 3. PORTFOLIO STATISTICS
    # --------------------------------

    stats = []

    for kpi in KPIS:
        values = df[kpi].dropna()

        stats.append({
            "KPI": kpi,
            "P10": values.quantile(0.10),
            "P25": values.quantile(0.25),
            "P50": values.quantile(0.50),
            "P75": values.quantile(0.75),
            "P90": values.quantile(0.90),
            "Mean": values.mean(),
            "Std": values.std()
        })

    portfolio_stats = pd.DataFrame(stats).round(2)

    portfolio_stats.to_csv(
        "output/portfolio_stats.csv",
        index=False
    )

    print("Created: output/portfolio_stats.csv")


if __name__ == "__main__":
    main()