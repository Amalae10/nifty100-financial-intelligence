import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

start_time = time.perf_counter()

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_sectors,
    get_pros_cons
)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_sectors,
    get_pros_cons
)

st.title("Company Profile")

companies =get_companies()
sectors =get_sectors()

# search
search=st.text_input(
    "Search company name or ticker",
    placeholder="example: INFY or Infosys"
)

if not search:
    st.info("Enter a company name or ticker to begin.")    
    st.stop()

search_lower=search.lower()

matches=companies[
    companies["id"].str.lower().str.contains(
        search_lower,na=False
    )
    |
    companies["company_name"].str.lower().str.contains(
        search_lower,na=False
    )
]

if matches.empty:
    st.warning("Ticker not found - please try another")
    st.stop()

options=(
    matches["company_name"]
    + " ( " +
    matches["id"]
    +")"
).tolist()

selcted=st.selectbox(
    "Select Company",options
)

ticker=selcted.split("(")[-1].replace(")","").strip()

company=companies[companies["id"]==ticker].iloc[0]

# company informations

sector_row=sectors[
    sectors["company_id"]==ticker
]

sector = (
    sector_row.iloc[0]["broad_sector"]
    if not sector_row.empty
    else "N/A"
)

sub_sector=(
    sector_row.iloc[0]["sub_sector"]
    if not sector_row.empty
    else "N/A"
)

st.subheader(company["company_name"])

c1,c2,c3=st.columns(3)

c1.write(f"**NSE Ticker:** {ticker}")
c2.write(f"**Sector:** {sector}")
c3.markdown(f"**Sub-Sector:** {sub_sector}")

about=company["about_company"]

if pd.notna(about):
    st.write(about)
else:
    st.write("company description not available.")

st.divider()

# Ratios

ratios=get_ratios(ticker)

if ratios.empty:
    st.warning("Financial ratio data unavailable.")
    st.stop()

ratios["year_num"]=pd.to_numeric(
    ratios["year"].astype(str).str.extract(r"(\d{4})")[0],
    errors="coerce"
)

ratios=ratios.dropna(subset=["year_num"])
ratios=ratios.sort_values("year_num")

latest=ratios.iloc[-1]

# kpi cards

def show_value(value,suffix=""):
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f}{suffix}"

k1,k2,k3,k4,k5,k6=st.columns(6)

k1.metric("ROE",show_value(latest["return_on_equity_pct"],"%"))

k2.metric("ROCE",show_value(latest["return_on_capital_pct"],"%"))

k3.metric("Net profit Margin",show_value(latest["net_profit_margin_pct"],"%"))

k4.metric("D/E",show_value(latest["debt_to_equity"]))

k5.metric("Revenue CAGR 5Y",show_value(latest["revenue_cagr_5yr"],"%"))

k6.metric(
    "FCF",
    f"₹{latest['free_cash_flow_cr']/1000:.1f}K Cr"
    if pd.notna(latest["free_cash_flow_cr"])
    else "N/A"
)

st.divider()

# profit & loss
pl=get_pl(ticker)

if not pl.empty:
    pl["year_num"]=pd.to_numeric(
        pl["year"].astype(str).str.extract(r"(\d{4})")[0],errors="coerce")

    pl=(pl.dropna(subset=["year_num"]).sort_values("year_num").tail(10))

    # Partial data warning
    if len(pl) < 10:
        st.info(
            f"Limited historical data available: "
            f"{len(pl)} years available for this company."
        )

    # Revenue + Net Profit bar chart
    st.subheader("Revenue & Net Profit - Historical Trend")

    fig_bar=go.Figure()

    fig_bar.add_bar(
        x=pl["year"],
        y=pl["sales"],
        name="Revenue"
    )

    fig_bar.add_bar(
        x=pl["year"],
        y=pl["net_profit"],
        name="Net Profit"
    )

    fig_bar.update_layout(
        barmode="group",
        xaxis_title="Year",
        yaxis_title="₹ Crore"
    )

    st.plotly_chart(
        fig_bar,
        width="stretch"
    )

else:
    st.info("Revenue and profit history not available.")

# ROE + ROCE

st.subheader("ROE & ROCE - Historical Trend")

trend=ratios.tail(10)
fig_line=make_subplots(
    specs=[[{"secondary_y":True}]]
)
fig_line.add_trace(
    go.Scatter(
        x=trend["year"],
        y=trend["return_on_equity_pct"],
        name="ROE",
        mode="lines+markers"
    ),
    secondary_y=False
)

fig_line.add_trace(
    go.Scatter(
        x=trend["year"],
        y=trend["return_on_capital_pct"],
        name="ROCE",
        mode="lines+markers"
    ),
    secondary_y=True
)

fig_line.update_yaxes(
    title_text="ROE (%)",
    secondary_y=False
)

fig_line.update_yaxes(
    title_text="ROCE (%)",
    secondary_y=True
)

fig_line.update_xaxes(
    title_text="Year"
)

st.plotly_chart(
    fig_line,
    width="stretch")

# PRONS & CONS

st.divider()
st.subheader("Pros & Cons")

pc = get_pros_cons(ticker)

if pc.empty:
    st.info("Pros and cons are not available for this company.")

else:
    pros_col, cons_col = st.columns(2)

    with pros_col:
        st.markdown("### ✅ Pros")

        for value in pc["pros"].dropna():
            st.success(str(value))

    with cons_col:
        st.markdown("### ❌ Cons")

        for value in pc["cons"].dropna():
            st.error(str(value))

load_time = time.perf_counter() - start_time
st.caption(f"Profile load time: {load_time:.2f} seconds")