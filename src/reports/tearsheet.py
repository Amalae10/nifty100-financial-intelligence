import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import Image

from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
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
OUT = Path("reports/tearsheets")
OUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#0B1F3A")


def get_company_data(ticker):
    with sqlite3.connect(DB) as conn:

        company = conn.execute(
            """
            SELECT id, company_name
            FROM companies
            WHERE id = ?
            """,
            (ticker,),
        ).fetchone()

        ratio = conn.execute(
        """
        SELECT * FROM financial_ratios
        WHERE company_id = ?
            AND year != 'TTM'
        ORDER BY
            CAST(SUBSTR(year, -4) AS INTEGER) DESC
        LIMIT 1
        """,
        (ticker,),
        ).fetchone()

        columns = [
            x[1]
            for x in conn.execute(
                "PRAGMA table_info(financial_ratios)"
            ).fetchall()
        ]

    return company, dict(zip(columns, ratio)) if ratio else {}


def fmt(value, suffix=""):
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.1f}{suffix}"
    except (ValueError, TypeError):
        return str(value)

def revenue_profit_chart(ticker):
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year, sales, net_profit
            FROM profitandloss
            WHERE company_id = ?
              AND year != 'TTM'
            """,
            conn,
            params=(ticker,),
        )

    df["year_num"] = pd.to_numeric(
        df["year"].str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    df = (
        df.dropna(subset=["year_num"])
        .sort_values("year_num")
        .tail(10)
    )
    if df.empty:
        return Paragraph(
            "Revenue / Net Profit: N/A",
            getSampleStyleSheet()["BodyText"],
        )

    drawing = Drawing(500, 170)

    chart = VerticalBarChart()
    chart.x = 45
    chart.y = 40
    chart.width = 420
    chart.height = 100

    chart.data = [
        df["sales"].tolist(),
        df["net_profit"].tolist(),
    ]

    chart.categoryAxis.categoryNames = (
        df["year_num"].astype(int).astype(str).tolist()
    )

    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.dy = -12

    # Allow negative Net Profit values to appear
    all_values = (
        df["sales"].fillna(0).tolist()
        + df["net_profit"].fillna(0).tolist()
    )

    min_val = min(all_values)
    max_val = max(all_values)

    chart.valueAxis.valueMin = min(0, min_val * 1.15)
    chart.valueAxis.valueMax = max_val * 1.10
    chart.valueAxis.labels.fontSize = 7

    chart.bars[0].fillColor = NAVY
    chart.bars[1].fillColor = colors.HexColor("#4F81BD")

    drawing.add(chart)

    legend = Legend()
    legend.x = 180
    legend.y = 155
    legend.fontSize = 8
    legend.colorNamePairs = [
        (NAVY, "Revenue"),
        (colors.HexColor("#4F81BD"), "Net Profit"),
    ]

    drawing.add(legend)

    return drawing

def roe_roce_chart(ticker):
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year,
                   return_on_equity_pct,
                   return_on_capital_pct
            FROM financial_ratios
            WHERE company_id = ?
              AND year != 'TTM'
            """,
            conn,
            params=(ticker,),
        )

    df["year_num"] = pd.to_numeric(
        df["year"].str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    df = (
        df.dropna(subset=["year_num"])
        .sort_values("year_num")
        .tail(10)
    )

    if df.empty:
        return Paragraph(
            "ROE / ROCE: N/A",
            getSampleStyleSheet()["BodyText"],
        )

    if (
        df["return_on_equity_pct"].isna().all()
        and df["return_on_capital_pct"].isna().all()
    ):
        style = getSampleStyleSheet()["BodyText"]
        style.fontSize = 10
        style.leading = 14
        style.alignment = 1

        return Paragraph(
            "<b>ROE / ROCE data not available</b><br/>"
            "Historical ROE and ROCE values are unavailable for this company.",
            style,
        )

    years = df["year_num"].astype(int).astype(str).tolist()

    roe = df["return_on_equity_pct"].fillna(0).tolist()
    roce = df["return_on_capital_pct"].fillna(0).tolist()

    drawing = Drawing(500, 160)

    # Dynamic axis ranges
    roe_min = min(roe)
    roe_max = max(roe)

    roce_min = min(roce)
    roce_max = max(roce)

    # =========================
    # LEFT AXIS — ROE
    # =========================

    left = HorizontalLineChart()

    left.x = 45
    left.y = 35
    left.width = 400
    left.height = 85

    left.data = [roe]

    left.categoryAxis.categoryNames = years
    left.categoryAxis.labels.angle = 45
    left.categoryAxis.labels.dy = -10

    # Allow negative ROE
    left.valueAxis.valueMin = min(0, roe_min - 5)
    left.valueAxis.valueMax = roe_max + 5
    left.valueAxis.labels.fontSize = 7

    left.lines[0].strokeColor = NAVY
    left.lines[0].strokeWidth = 1.5

    drawing.add(left)

    # =========================
    # RIGHT AXIS — ROCE
    # =========================

    right = HorizontalLineChart()

    right.x = 45
    right.y = 35
    right.width = 400
    right.height = 85

    right.data = [roce]

    right.categoryAxis.categoryNames = years

    # Hide duplicate X-axis labels
    right.categoryAxis.labels.fontSize = 0
    right.categoryAxis.strokeColor = colors.transparent

    # Allow negative ROCE
    right.valueAxis.valueMin = min(0, roce_min - 5)
    right.valueAxis.valueMax = roce_max + 5

    # Right-side Y axis
    right.valueAxis.joinAxisMode = "right"
    right.valueAxis.labels.fontSize = 7

    right.lines[0].strokeColor = colors.HexColor("#4F81BD")
    right.lines[0].strokeWidth = 1.5

    drawing.add(right)

    # =========================
    # LEGEND
    # =========================

    legend = Legend()
    legend.x = 190
    legend.y = 145
    legend.fontSize = 8
    legend.dx = 8
    legend.dy = 8
    legend.deltay = 10

    legend.colorNamePairs = [
        (NAVY, "ROE"),
        (colors.HexColor("#4F81BD"), "ROCE"),
    ]

    drawing.add(legend)

    return drawing

def balance_sheet_chart(ticker):
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year,
                   equity_capital,
                   reserves,
                   borrowings,
                   other_liabilities
            FROM balancesheet
            WHERE company_id = ?
            """,
            conn,
            params=(ticker,),
        )

    if df.empty:
        return Paragraph(
            "Balance Sheet: N/A",
            getSampleStyleSheet()["BodyText"],
        )

    # Parse different year formats:
    # Mar 2024, Sep 2024, Mar-24, 2024 etc.
    def parse_year(x):
        x = str(x).strip()

        for fmt in ("%b %Y", "%b-%y", "%Y", "%Y-%m-%d"):
            try:
                return pd.to_datetime(x, format=fmt)
            except ValueError:
                pass

        return pd.NaT

    df["sort_year"] = df["year"].apply(parse_year)

    df = (
        df.dropna(subset=["sort_year"])
        .sort_values("sort_year")
        .tail(10)
    )

    if df.empty:
        return Paragraph(
            "Balance Sheet: N/A",
            getSampleStyleSheet()["BodyText"],
        )

    # Equity = Equity Capital + Reserves
    df["equity"] = (
        df["equity_capital"].fillna(0)
        + df["reserves"].fillna(0)
    )

    drawing = Drawing(500, 165)

    chart = VerticalBarChart()
    chart.x = 45
    chart.y = 40
    chart.width = 420
    chart.height = 95

    chart.data = [
        df["equity"].tolist(),
        df["borrowings"].fillna(0).tolist(),
        df["other_liabilities"].fillna(0).tolist(),
    ]

    chart.categoryAxis.style = "stacked"

    # Display actual financial-year labels
    chart.categoryAxis.categoryNames = df["year"].astype(str).tolist()

    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.dy = -12
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontSize = 7

    chart.bars[0].fillColor = NAVY
    chart.bars[1].fillColor = colors.HexColor("#4F81BD")
    chart.bars[2].fillColor = colors.HexColor("#A5A5A5")

    drawing.add(chart)

    legend = Legend()
    legend.x = 330
    legend.y = 195
    legend.fontSize = 7

    legend.colorNamePairs = [
        (NAVY, "Equity"),
        (colors.HexColor("#4F81BD"), "Borrowings"),
        (colors.HexColor("#A5A5A5"), "Other Liabilities"),
    ]

    drawing.add(legend)

    return drawing

def cashflow_waterfall(ticker):

    from reportlab.graphics.shapes import Drawing, Rect, Line, String

    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year,
                   operating_activity,
                   investing_activity,
                   financing_activity,
                   net_cash_flow
            FROM cashflow
            WHERE company_id = ?
            """,
            conn,
            params=(ticker,),
        )

    if df.empty:
        style = getSampleStyleSheet()["BodyText"]
        style.fontSize = 10
        style.leading = 14
        style.alignment = 1

        return Paragraph(
            "<b>Cash flow data not available</b><br/>"
            "No cash flow records are available for this company.",
            style,
        )
    # Convert Mar-24 -> date for correct sorting
    def parse_cf_year(x):
        x = str(x).strip()

        for fmt in ("%b-%y", "%Y", "%b %Y", "%Y-%m-%d"):
            try:
                return pd.to_datetime(x, format=fmt)
            except ValueError:
                pass

        return pd.NaT


    df["sort_year"] = df["year"].apply(parse_cf_year)

    df = df.dropna(subset=["sort_year"]).sort_values("sort_year")

    if df.empty:
        style = getSampleStyleSheet()["BodyText"]
        style.fontSize = 10
        style.leading = 14
        style.alignment = 1

        return Paragraph(
            "<b>Cash flow data not available</b><br/>"
            "No cash flow records are available for this company.",
            style,
        )

    latest = df.iloc[-1]

    values = [
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        latest["net_cash_flow"],
    ]

    names = ["CFO", "CFI", "CFF", "Net Cash"]

    values = [
        0 if pd.isna(v) else float(v)
        for v in values
    ]

    d = Drawing(500, 210)

    baseline = 110
    max_height = 70
    max_abs = max(abs(v) for v in values) or 1

    xs = [65, 180, 295, 410]
    bar_width = 65

    # Zero line
    d.add(Line(30, baseline, 480, baseline))

    for x, value, name in zip(xs, values, names):

        height = abs(value) / max_abs * max_height

        # Small values should still be visible
        if value != 0:
            height = max(height, 12)

        if value >= 0:
            y = baseline
            value_y = baseline + height + 7
        else:
            y = baseline - height
            value_y = y - 13

        d.add(
            Rect(
                x,
                y,
                bar_width,
                height,
                fillColor=NAVY,
                strokeColor=NAVY,
            )
        )

        d.add(
            String(
                x + bar_width / 2,
                value_y,
                f"{value:,.0f}",
                textAnchor="middle",
                fontSize=9,
            )
        )

        d.add(
            String(
                x + bar_width / 2,
                15,
                name,
                textAnchor="middle",
                fontSize=9,
            )
        )

    return d

def intelligence_section(ticker, styles):
    pc = pd.read_csv("output/pros_cons_generated.csv")
    cf = pd.read_excel("output/cashflow_intelligence.xlsx")

    company_pc = pc[pc["company_id"] == ticker]

    pros = (
        company_pc[company_pc["type"] == "pro"]
        .sort_values("confidence_pct", ascending=False)
        .head(3)
    )

    cons = (
        company_pc[company_pc["type"] == "con"]
        .sort_values("confidence_pct", ascending=False)
        .head(3)
    )

    # Pros
    pro_text = "<b><font color='green'>Pros</font></b><br/>"

    if pros.empty:
        pro_text += "No qualifying pro signal generated."
    else:
        for text in pros["text"]:
            pro_text += f"• {text}<br/>"

    # Cons
    con_text = "<b><font color='red'>Cons</font></b><br/>"

    if cons.empty:
        con_text += "No qualifying con signal generated."
    else:
        for text in cons["text"]:
            con_text += f"• {text}<br/>"

    table = Table(
        [[
            Paragraph(pro_text, styles["BodyText"]),
            Paragraph(con_text, styles["BodyText"]),
        ]],
        colWidths=[90 * mm, 90 * mm],
    )

    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        # Day 33 requirement
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
    ]))

    # Capital allocation
    row = cf[cf["company_id"] == ticker]

    allocation_label = (
        row.iloc[0]["capital_allocation_label"]
        if not row.empty
        else "Insufficient Data"
    )

    badge = Table(
        [[
            Paragraph(
                f"<b>Capital Allocation:</b> {allocation_label}",
                styles["BodyText"],
            )
        ]],
        colWidths=[180 * mm],
    )

    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
    ]))

    return table, badge

def financial_history_table(ticker, styles):
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year,
                   return_on_equity_pct,
                   return_on_capital_pct,
                   operating_profit_margin_pct,
                   debt_to_equity,
                   free_cash_flow_cr,
                   revenue_cagr_5yr,
                   pe_ratio,
                   composite_quality_score
            FROM financial_ratios
            WHERE company_id = ?
              AND year != 'TTM'
            ORDER BY CAST(SUBSTR(year, -4) AS INTEGER)
            """,
            conn,
            params=(ticker,),
        )

    if df.empty:
        return Paragraph(
            "Financial history not available.",
            styles["BodyText"],
        )

    data = [[
        "Year", "ROE %", "ROCE %", "OPM %",
        "D/E", "FCF Cr", "Rev CAGR 5Y %",
        "P/E", "Quality"
    ]]

    for _, row in df.tail(10).iterrows():
        data.append([
            str(row["year"]),
            fmt(row["return_on_equity_pct"]),
            fmt(row["return_on_capital_pct"]),
            fmt(row["operating_profit_margin_pct"]),
            fmt(row["debt_to_equity"]),
            fmt(row["free_cash_flow_cr"]),
            fmt(row["revenue_cagr_5yr"]),
            fmt(row["pe_ratio"]),
            fmt(row["composite_quality_score"]),
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            20 * mm, 18 * mm, 18 * mm,
            18 * mm, 16 * mm, 20 * mm,
            25 * mm, 18 * mm, 22 * mm
        ],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.whitesmoke]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    return table

def performance_png(ticker):
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql(
            """
            SELECT year, sales, net_profit
            FROM profitandloss
            WHERE company_id = ?
              AND year != 'TTM'
            """,
            conn,
            params=(ticker,),
        )

    df["year_num"] = pd.to_numeric(
        df["year"].str.extract(r"(20\d{2})")[0],
        errors="coerce",
    )

    df = df.dropna(subset=["year_num"]).sort_values("year_num").tail(10)

    if df.empty:
        return None

    chart_dir = OUT / "_charts"
    chart_dir.mkdir(exist_ok=True)

    path = chart_dir / f"{ticker}_performance.png"

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=180)

    ax.plot(df["year_num"], df["sales"], marker="o", label="Revenue")
    ax.plot(df["year_num"], df["net_profit"], marker="o", label="Net Profit")

    ax.set_title(f"{ticker} - Financial Performance")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rs Crore")
    ax.grid(alpha=0.25)
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)

    return path

def build_tearsheet(ticker):
    company, r = get_company_data(ticker)

    if not company:
        raise ValueError(f"Unknown ticker: {ticker}")

    company_name = company[1]
    pdf_path = OUT / f"{ticker}_tearsheet.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.white

    story = []

    # ================= PAGE 1 =================

    # Navy header
    header = Table(
        [[
            Paragraph(
                f"<b>{company_name}</b><br/>{ticker}",
                styles["Title"],
            )
        ]],
        colWidths=[186 * mm],
        rowHeights=[22 * mm],
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
    ]))

    story.append(header)
    story.append(Spacer(1, 5 * mm))

    # 6 KPI tiles
    kpis = [
        ("ROE", fmt(r.get("return_on_equity_pct"), "%")),
        ("ROCE", fmt(r.get("return_on_capital_pct"), "%")),
        ("Net Margin", fmt(r.get("net_profit_margin_pct"), "%")),
        ("Debt / Equity", fmt(r.get("debt_to_equity"))),
        ("Revenue CAGR 5Y", fmt(r.get("revenue_cagr_5yr"), "%")),
        ("Quality Score", fmt(r.get("composite_quality_score"))),
    ]

    cells = []

    for label, value in kpis:
        cells.append(
            Paragraph(
                f"<b>{label}</b><br/>"
                f"<font size='14'>{value}</font>",
                styles["BodyText"],
            )
        )

    kpi_table = Table(
        [
            cells[:3],
            cells[3:],
        ],
        colWidths=[60 * mm] * 3,
        rowHeights=[22 * mm] * 2,
    )

    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
    ]))

    story.append(kpi_table)
    story.append(Spacer(1, 4 * mm))

    # Revenue + Net Profit
    story.append(
        Paragraph(
            "<b>10-Year Revenue & Net Profit</b>",
            styles["Heading2"],
        )
    )

    story.append(revenue_profit_chart(ticker))
    story.append(Spacer(1, 1 * mm))

    # ROE + ROCE
    story.append(
        Paragraph(
            "<b>ROE & ROCE Trend</b>",
            styles["Heading2"],
        )
    )

    story.append(roe_roce_chart(ticker))

    # ================= PAGE 2 =================

    story.append(PageBreak())

    # Balance Sheet
    story.append(
        Paragraph(
            "<b>Balance Sheet Composition</b>",
            styles["Heading2"],
        )
    )

    story.append(balance_sheet_chart(ticker))
    story.append(Spacer(1, 2 * mm))

    # Cash Flow
    story.append(
        Paragraph(
            "<b>Cash Flow Waterfall — Latest Year</b>",
            styles["Heading2"],
        )
    )

    story.append(cashflow_waterfall(ticker))

    story.append(Spacer(1, 2 * mm))

    pros_cons, allocation_badge = intelligence_section(
        ticker,
        styles,
    )

    story.append(pros_cons)
    story.append(Spacer(1, 2 * mm))
    story.append(allocation_badge)

    # ================= PAGE 3 =================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "<b>10-Year Financial & KPI History</b>",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 3 * mm))
    story.append(financial_history_table(ticker, styles))

    story.append(Spacer(1, 5 * mm))

    chart_path = performance_png(ticker)

    if chart_path:
        story.append(
            Paragraph(
                "<b>Financial Performance Trend</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Image(
                str(chart_path),
                width=180 * mm,
                height=90 * mm,
            )
        )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "<b>Data Note</b><br/>"
            "Metrics are calculated from the financial information available "
            "in the N100 Financial Intelligence database. Companies with shorter "
            "listing histories may contain fewer historical periods.",
            styles["BodyText"],
        )
    )

    # Build PDF
    doc.build(story)

    print("Created:", pdf_path)


if __name__ == "__main__":
    skipped = []

    with sqlite3.connect(DB) as conn:
        companies = pd.read_sql(
            """
            SELECT c.id AS company_id,
                   COUNT(DISTINCT p.year) AS years
            FROM companies c
            LEFT JOIN profitandloss p
                ON c.id = p.company_id
                AND p.year != 'TTM'
            GROUP BY c.id
            """,
            conn,
        )

        for _, row in companies.iterrows():
            ticker = row["company_id"]
            years = row["years"]

            try:
                    build_tearsheet(ticker)
            except Exception as e:
                    print(f"ERROR: {ticker} - {e}")

    # Save genuine data skips
    pd.DataFrame(
        skipped,
        columns=[
            "company_id",
            "years_available",
            "reason",
        ],
    ).to_csv(
        "output/skipped_tearsheets.csv",
        index=False,
    )

    print("\nBatch generation complete.")
    print("Skipped:", len(skipped))
