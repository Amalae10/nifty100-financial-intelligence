import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH="nifty100.db"

st.title("Sector Analysis")

# Load data

@st.cache_data(ttl=600)
def load_sector_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            pl.sales AS revenue,
            fr.return_on_equity_pct AS roe,
            fr.return_on_capital_pct AS roce,
            fr.operating_profit_margin_pct AS opm,
            mc.market_cap_crore AS market_cap

        FROM companies c

        LEFT JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN profitandloss pl
            ON c.id = pl.company_id
            AND pl.year = 'Mar 2024'

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
            AND fr.year = 'Mar 2024'

        LEFT JOIN market_cap mc
            ON c.id = mc.company_id
            AND mc.year = '2024'
    """, conn)

df=load_sector_data()

# sector dropdown

sectors=sorted(
    df["broad_sector"].dropna().unique()
)

selected_sector=st.selectbox("Select Sector",sectors)

sector_df=df[df["broad_sector"]==selected_sector].copy()

# clean numeric data

for col in["revenue","roe","roce","opm","market_cap"]:
    sector_df[col]=pd.to_numeric(sector_df[col],errors="coerce")

# bubble chart

st.subheader(f"{selected_sector} - company Analysis")

bubble_df=sector_df.dropna(
    subset=["revenue","roe","market_cap"]
)

if bubble_df.empty:
    st.warning("No data available for this sector.")

else:
    fig = px.scatter(
        bubble_df,
        x="revenue",
        y="roe",
        size="market_cap",
        color="sub_sector",
        hover_name="company_name",
        hover_data={
            "company_id": True,
            "revenue": ":.2f",
            "roe": ":.2f",
            "market_cap": ":.2f"
        },
        labels={
            "revenue": "Revenue (₹ Cr)",
            "roe": "ROE (%)",
            "market_cap": "Market Cap (₹ Cr)",
            "sub_sector": "Sub-sector"
        },
        title=f"{selected_sector} — Revenue vs ROE"
    )

    st.plotly_chart(fig, width="stretch")


# Sector Median KPI Bar Chart

st.subheader("Sector Median KPI")

metric_options = {
    "Revenue": ("revenue", "₹ Cr"),
    "ROE": ("roe", "%"),
    "Market Cap": ("market_cap", "₹ Cr")
}

selected_kpi = st.selectbox(
    "Select Median KPI",
    list(metric_options.keys())
)

column, unit = metric_options[selected_kpi]

median_value = sector_df[column].median()

median_chart = pd.DataFrame({
    "Sector": [selected_sector],
    "Median": [median_value]
})

fig_median = px.bar(
    median_chart,
    x="Sector",
    y="Median",
    text="Median",
    title=f"{selected_sector} — Median {selected_kpi}"
)

if unit == "%":
    label = f"{median_value:.2f}%"
    y_title = f"{selected_kpi} (%)"
else:
    label = f"₹{median_value:,.2f} Cr"
    y_title = f"{selected_kpi} (₹ Cr)"

fig_median.update_traces(
    text=[label],
    textposition="outside"
)

fig_median.update_yaxes(
    range=[0, median_value * 1.25]
)

fig_median.update_layout(
    yaxis_title=y_title,
    xaxis_title=""
)

st.plotly_chart(
    fig_median,
    width="stretch"
)