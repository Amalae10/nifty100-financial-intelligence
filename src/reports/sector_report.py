import re
import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

DB = "nifty100.db"
OUT = Path("reports/sector")
OUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#0B1F3A")


# 8 required metrics
METRICS = {
    "ROE %": "return_on_equity_pct",
    "ROCE %": "return_on_capital_pct",
    "Net Margin %": "net_profit_margin_pct",
    "Debt/Equity": "debt_to_equity",
    "Revenue CAGR 5Y %": "revenue_cagr_5yr",
    "PAT CAGR 5Y %": "pat_cagr_5yr",
    "CFO/PAT": "cfo_pat_ratio",
    "Quality Score": "composite_quality_score",
}


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def fmt(value):
    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return str(value)


def get_sector_data(sector):
    with sqlite3.connect(DB) as conn:

        companies = pd.read_sql(
            """
            SELECT c.id AS company_id
            FROM companies c
            JOIN sectors s
              ON c.id = s.company_id
            WHERE s.broad_sector = ?
            ORDER BY c.id
            """,
            conn,
            params=(sector,),
        )

        ratios = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE year != 'TTM'
            """,
            conn,
        )

    # Extract year
    ratios["year_num"] = pd.to_numeric(
        ratios["year"].str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    # Latest annual row for every company
    latest = (
        ratios
        .dropna(subset=["year_num"])
        .sort_values("year_num")
        .groupby("company_id")
        .tail(1)
    )

    # Merge sector companies with latest ratios
    df = companies.merge(
        latest,
        on="company_id",
        how="left",
    )

    return df

def build_sector_report(sector):
    df = get_sector_data(sector)

    filename = OUT / f"{safe_name(sector)}_report.pdf"

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    # -------------------------
    # HEADER
    # -------------------------

    title = Paragraph(
        f"<b>{sector} — Sector Report</b>",
        styles["Title"],
    )

    story.append(title)
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"Companies in sector: <b>{len(df)}</b>",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 12))

    # -------------------------
    # MEDIAN KPIs
    # -------------------------

    story.append(
        Paragraph(
            "<b>Sector Median KPIs</b>",
            styles["Heading2"],
        )
    )

    median_data = []

    for label, column in METRICS.items():
        median = pd.to_numeric(
            df[column],
            errors="coerce",
        ).median()

        median_data.append([
            label,
            fmt(median),
        ])

    median_table = Table(
        median_data,
        colWidths=[55 * mm, 30 * mm],
    )

    median_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), NAVY),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),

            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )

    story.append(median_table)
    story.append(Spacer(1, 8))

    # -------------------------
    # COMPANY TABLE
    # -------------------------

    story.append(
        Paragraph(
            "<b>Companies — 8 Key Metrics</b>",
            styles["Heading2"],
        )
    )

    headers = [
        "Ticker",
        "ROE %",
        "ROCE %",
        "Net Margin %",
        "D/E",
        "Revenue CAGR 5Y %",
        "PAT CAGR 5Y %",
        "CFO/PAT",
        "Quality Score",
    ]

    table_data = [headers]

    for _, row in df.iterrows():

        table_data.append([
            Paragraph(str(row["company_id"]), styles["BodyText"]),
            fmt(row["return_on_equity_pct"]),
            fmt(row["return_on_capital_pct"]),
            fmt(row["net_profit_margin_pct"]),
            fmt(row["debt_to_equity"]),
            fmt(row["revenue_cagr_5yr"]),
            fmt(row["pat_cagr_5yr"]),
            fmt(row["cfo_pat_ratio"]),
            fmt(row["composite_quality_score"]),
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
        32 * mm,   # Ticker - wider
        18 * mm,   # ROE
        18 * mm,   # ROCE
        22 * mm,   # Net Margin
        16 * mm,   # D/E
        28 * mm,   # Revenue CAGR
        26 * mm,   # PAT CAGR
        19 * mm,   # CFO/PAT
        25 * mm,   # Quality Score
    ],
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),

            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("FONTSIZE", (0, 0), (-1, -1), 7),

            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ])
    )

    story.append(table)

    doc.build(story)

    print(f"Created: {filename}")


def main():
    with sqlite3.connect(DB) as conn:
        sectors = pd.read_sql(
            """
            SELECT DISTINCT broad_sector
            FROM sectors
            WHERE broad_sector IS NOT NULL
            ORDER BY broad_sector
            """,
            conn,
        )

    for sector in sectors["broad_sector"]:
        build_sector_report(sector)

    print("\nSector report generation complete.")
    print("Reports created:", len(sectors))


if __name__ == "__main__":
    main()