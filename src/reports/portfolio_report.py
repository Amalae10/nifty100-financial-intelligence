import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

DB = "nifty100.db"

OUT = Path("reports/portfolio")
OUT.mkdir(parents=True, exist_ok=True)

PDF = OUT / "portfolio_summary.pdf"

NAVY = colors.HexColor("#0B1F3A")


METRICS = {
    "ROE %": "return_on_equity_pct",
    "ROCE %": "return_on_capital_pct",
    "Net Profit Margin %": "net_profit_margin_pct",
    "Debt / Equity": "debt_to_equity",
    "Revenue CAGR 5Y %": "revenue_cagr_5yr",
    "Quality Score": "composite_quality_score",
}


def fmt(value):
    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return str(value)


def trend(current, previous, lower_is_better=False):
    if pd.isna(current) or pd.isna(previous):
        return "N/A"

    current = float(current)
    previous = float(previous)

    # Flat if change is within 2%
    if previous == 0:
        change = current - previous
        flat = abs(change) <= 0.02
    else:
        change_pct = ((current - previous) / abs(previous)) * 100
        flat = abs(change_pct) <= 2

    if flat:
        return "→"

    improved = current > previous

    # Debt/Equity: lower value is improvement
    if lower_is_better:
        improved = current < previous

    return "↑" if improved else "↓"


def get_data():
    with sqlite3.connect(DB) as conn:

        companies = pd.read_sql(
            """
            SELECT
                c.id AS company_id,
                c.company_name,
                s.broad_sector
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            ORDER BY c.id
            """,
            conn,
        )

        ratios = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE year != 'TTM'
            """,
            conn,
        )

    ratios["year_num"] = pd.to_numeric(
        ratios["year"].str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    ratios = (
        ratios
        .dropna(subset=["year_num"])
        .sort_values(["company_id", "year_num"])
    )

    return companies, ratios


def build_portfolio():
    companies, ratios = get_data()

    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    total = len(companies)

    for number, (_, company) in enumerate(
        companies.iterrows(),
        start=1,
    ):
        ticker = company["company_id"]

        company_ratios = (
            ratios[ratios["company_id"] == ticker]
            .sort_values("year_num")
        )

        if company_ratios.empty:
            latest = None
            previous = None
        else:
            latest = company_ratios.iloc[-1]

            previous = (
                company_ratios.iloc[-2]
                if len(company_ratios) >= 2
                else None
            )

        # -------------------------
        # HEADER
        # -------------------------

        header = Table(
            [[
                Paragraph(
                    f"<font color='white'><b>"
                    f"{company['company_name']}"
                    f"</b></font><br/>"
                    f"<font color='white'>{ticker}</font>",
                    styles["Title"],
                )
            ]],
            colWidths=[174 * mm],
        )

        header.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ])
        )

        story.append(header)
        story.append(Spacer(1, 10))

        sector = company["broad_sector"]

        if pd.isna(sector):
            sector = "N/A"

        story.append(
            Paragraph(
                f"<b>Sector:</b> {sector}",
                styles["Heading2"],
            )
        )

        story.append(Spacer(1, 12))

        # -------------------------
        # TOP 6 KPI TABLE
        # -------------------------

        kpi_data = [
            ["KPI", "Latest", "Trend"]
        ]

        for label, column in METRICS.items():

            if latest is None:
                current = None
                old = None
            else:
                current = latest[column]

                old = (
                    previous[column]
                    if previous is not None
                    else None
                )

            arrow = trend(
                current,
                old,
                lower_is_better=(column == "debt_to_equity"),
            )

            kpi_data.append([
                label,
                fmt(current),
                arrow,
            ])

        kpi_table = Table(
            kpi_data,
            colWidths=[
                85 * mm,
                40 * mm,
                30 * mm,
            ],
        )

        kpi_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("FONTSIZE", (0, 0), (-1, -1), 10),

                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ])
        )

        story.append(
            Paragraph(
                "<b>Top 6 KPIs</b>",
                styles["Heading2"],
            )
        )

        story.append(kpi_table)
        story.append(Spacer(1, 15))

        # -------------------------
        # TREND EXPLANATION
        # -------------------------

        story.append(
            Paragraph(
                "<b>Trend:</b> "
                "↑ Improved &nbsp;&nbsp; "
                "↓ Declined &nbsp;&nbsp; "
                "→ Flat (within 2%)",
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 8))

        year = (
            int(latest["year_num"])
            if latest is not None
            else "N/A"
        )

        story.append(
            Paragraph(
                f"Latest financial year: <b>{year}</b>",
                styles["BodyText"],
            )
        )

        # Exactly one company per page
        if number < total:
            story.append(PageBreak())

    doc.build(story)

    print(f"Created: {PDF}")
    print(f"Companies: {total}")
    print(f"Expected pages: {total}")


if __name__ == "__main__":
    build_portfolio()
    