import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

DB_PATH="nifty100.db"

st.title("Trend Analysis")

# load companies

@st.cache_data(ttl=600)
def load_companies():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT id AS company_id,company_name
            FROM companies
            ORDER BY company_name
            """,conn)

companies=load_companies()

# company search

company_options = (
    companies["company_id"]
    + " - "
    + companies["company_name"]
)

selected_company = st.selectbox(
    "Search Company",
    company_options
)

company_id = selected_company.split(" - ", 1)[0]


# load 10-year data
@st.cache_data(ttl=600)
def load_trends(company_id):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT
                pl.year,
                pl.sales AS revenue,
                pl.net_profit,
                fr.return_on_equity_pct AS roe,
                fr.return_on_capital_pct AS roce,
                fr.operating_profit_margin_pct AS opm,
                fr.debt_to_equity AS de
            FROM profitandloss pl
            LEFT JOIN financial_ratios fr
                ON pl.company_id = fr.company_id
                AND pl.year = fr.year
            WHERE pl.company_id = ?
        """, conn, params=(company_id,))


df = load_trends(company_id)

# year cleaning

df["year_num"]=(
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year_num"]=pd.to_numeric(df["year_num"],errors="coerce")

df=(df.dropna(subset=["year_num"]).sort_values("year_num").tail(10))

# metric selector

metrics={
    "Revenue":"revenue",
    "Net Profit":"net_profit",
    "ROE":"roe",
    "ROCE":"roce",
    "OPM":"opm",
    "Debt to Equity":"de"
}
selected_metrics = st.multiselect(
    "Select Metrics (Maximum 3)",
    list(metrics.keys()),
    default=["Revenue"],
    max_selections=3
)

# Check whether selected metrics have any usable data
selected_columns = [
    metrics[name]
    for name in selected_metrics
]

available_data = df[selected_columns].apply(
    pd.to_numeric,
    errors="coerce"
)

if available_data.dropna(how="all").empty:
    st.info("Selected metrics are not available for this company.")
    st.stop()

# trend chart

fig = go.Figure()

for metric_name in selected_metrics:

    column = metrics[metric_name]

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    # skip metric if no data is available
    if values.dropna().empty:
        st.info(f"{metric_name} is not available for this company.")
        continue


    # YoY %
    previous = values.shift(1)

    yoy = ((values - previous) / previous.abs()) * 100

    yoy = yoy.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # Normalize only for chart display
    min_val = values.min()
    max_val = values.max()

    if pd.isna(min_val) or pd.isna(max_val):
        normalized = values

    elif max_val == min_val:
        normalized = pd.Series(50.0, index=values.index)

        st.info(
            f"{metric_name} has no change during the selected period "
            f"(value: {min_val:.2f})."
        )

    else:
        normalized = (
            (values - min_val)
            / (max_val - min_val)
        ) * 100

    text = [
        "" if pd.isna(x) else f"{x:+.1f}%"
        for x in yoy
    ]

    fig.add_trace(
        go.Scatter(
            x=df["year_num"],
            y=normalized,
            mode="lines+markers+text",
            name=metric_name,
            text=text,
            textposition="top center",

            customdata=values,

            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Year: %{x}<br>"
                "Actual Value: %{customdata:.2f}"
                "<extra></extra>"
            )
        )
    )


fig.update_layout(
    title=f"10-Year Financial Trend — {company_id}",
    xaxis_title="Year",
    yaxis_title="Relative Trend (0-100)",
    hovermode="x"
)

st.plotly_chart(
    fig,
    width="stretch"
)