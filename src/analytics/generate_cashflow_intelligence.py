import sqlite3
from pathlib import Path
import pandas as pd

from src.analytics.cashflow_kpis import (
    cfo_pat_ratio,
    cfo_quality,
    capex_intensity,
    fcf_conversion,
    allocation,
    distress_signal,
    deleveraging,
)

DB = "nifty100.db"
OUT = Path("output")
OUT.mkdir(exist_ok=True)


def main():
    with sqlite3.connect(DB) as conn:
        cf = pd.read_sql("SELECT * FROM cashflow", conn)
        pl = pd.read_sql("SELECT * FROM profitandloss", conn)
        bs = pd.read_sql("SELECT * FROM balancesheet", conn)
        sectors = pd.read_sql(
            "SELECT company_id, broad_sector FROM sectors", conn
        )
        ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
        companies = pd.read_sql("SELECT id FROM companies", conn)

    # Merge annual financial data
    df = (
        cf.merge(
            pl[["company_id", "year", "sales",
                "operating_profit", "net_profit"]],
            on=["company_id", "year"],
            how="left",
        )
        .merge(
            bs[["company_id", "year", "borrowings"]],
            on=["company_id", "year"],
            how="left",
        )
    )

    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    rows = []
    alerts = []

    for company in companies["id"].astype(str):
        g = df[df["company_id"] == company].sort_values(
            "year_num"
        ).copy()

        # Company has no cash-flow records
        if g.empty:
            sector_row = sectors[
                sectors["company_id"] == company
            ]

            sector = (
                sector_row.iloc[0]["broad_sector"]
                if not sector_row.empty else None
            )

            rows.append({
                "company_id": company,
                "sector": sector,
                "cfo_quality_score": None,
                "cfo_quality_label": "Insufficient Data",
                "capex_intensity_pct": None,
                "capex_label": "Insufficient Data",
                "fcf_cagr_5yr": None,
                "fcf_conversion_pct": None,
                "distress_flag": False,
                "deleveraging_flag": False,
                "capital_allocation_label": "Insufficient Data",
            })

            continue

        latest = g.iloc[-1]
        previous = g.iloc[-2] if len(g) >= 2 else None

        # CFO / PAT — latest 5 years
        ratios_5y = []

        for _, r in g.tail(5).iterrows():
            value = cfo_pat_ratio(
                r["operating_activity"],
                r["net_profit"],
            )
            if value is not None and pd.notna(value):
                ratios_5y.append(value)

        quality_score = (
            sum(ratios_5y) / len(ratios_5y)
            if ratios_5y else None
        )

        quality_label = cfo_quality(ratios_5y)

        # CapEx intensity — latest year
        if pd.notna(latest["sales"]) and latest["sales"] != 0:
            capex_pct = (
                abs(latest["investing_activity"])
                / latest["sales"] * 100
            )
        else:
            capex_pct = None

        capex_label = capex_intensity(
            latest["investing_activity"],
            latest["sales"],
        )

        # FCF
        latest_fcf = (
            latest["operating_activity"]
            + latest["investing_activity"]
        )

        conversion = fcf_conversion(
            latest_fcf,
            latest["operating_profit"],
        )

        # Distress
        distress = distress_signal(
            latest["operating_activity"],
            latest["financing_activity"],
        )

        # Deleveraging
        if previous is not None:
            delev = deleveraging(
                latest["financing_activity"],
                latest["borrowings"],
                previous["borrowings"],
            )
        else:
            delev = False

        # Capital allocation
        _, allocation_label = allocation(
            latest["operating_activity"],
            latest["investing_activity"],
            latest["financing_activity"],
            quality_score,
        )

        # Existing FCF CAGR
        rr = ratios[
            (ratios["company_id"] == company)
            & (ratios["year"].astype(str) == str(latest["year"]))
        ]

        fcf_cagr = (
            rr.iloc[0]["fcf_cagr_5yr"]
            if not rr.empty and "fcf_cagr_5yr" in rr.columns
            else None
        )

        sector_row = sectors[
            sectors["company_id"] == company
        ]

        sector = (
            sector_row.iloc[0]["broad_sector"]
            if not sector_row.empty else None
        )

        rows.append({
            "company_id": company,
            "sector": sector,
            "cfo_quality_score": quality_score,
            "cfo_quality_label": quality_label,
            "capex_intensity_pct": capex_pct,
            "capex_label": capex_label,
            "fcf_cagr_5yr": fcf_cagr,
            "fcf_conversion_pct": conversion,
            "distress_flag": distress,
            "deleveraging_flag": delev,
            "capital_allocation_label": allocation_label,
        })

        if distress:
            alerts.append({
                "company_id": company,
                "cfo_value": latest["operating_activity"],
                "cff_value": latest["financing_activity"],
                "latest_net_profit": latest["net_profit"],
            })

    result = pd.DataFrame(rows)
    distress_df = pd.DataFrame(
        alerts,
        columns=[
            "company_id",
            "cfo_value",
            "cff_value",
            "latest_net_profit",
        ],
    )

    result.to_excel(
        OUT / "cashflow_intelligence.xlsx",
        index=False,
    )

    distress_df.to_csv(
        OUT / "distress_alerts.csv",
        index=False,
    )

    print("Companies processed:", len(result))
    print("Distress signals:", result["distress_flag"].sum())
    print("Deleveraging signals:", result["deleveraging_flag"].sum())

    print("\nCreated:")
    print("output/cashflow_intelligence.xlsx")
    print("output/distress_alerts.csv")


if __name__ == "__main__":
    main()