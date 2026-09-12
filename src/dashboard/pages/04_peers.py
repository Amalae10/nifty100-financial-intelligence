import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import sqlite3 
import streamlit as st
import plotly.graph_objects as go

DB_PATH="nifty100.db"

st.title("peer comparison")

# load data

@st.cache_data(ttl=600)
def load_peer_groups():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT
                pg.peer_group_name,
                pg.company_id,
                pg.is_benchmark,
                c.company_name
            FROM peer_groups pg
            LEFT JOIN companies c
                ON pg.company_id = c.id
            ORDER BY pg.peer_group_name,pg.company_id
            """,conn)

@st.cache_data(ttl=600)
def load_percentiles(group_name):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT *
            FROM peer_percentiles
            WHERE peer_group_name=?
        """,conn,params=(group_name,))

groups_df=load_peer_groups()

if groups_df.empty:
    st.warning("No peer-group data available.")
    st.stop()

# peer group selector

group_names=sorted(groups_df["peer_group_name"].dropna().unique())

selected_group=st.sidebar.selectbox(
    "peer Group",
    group_names
)

group_companies=groups_df[
    groups_df["peer_group_name"]== selected_group].copy()

# company selector

company_options = {
    f"{row['company_name']} ({row['company_id']})":
        row["company_id"]
    for _, row in group_companies.iterrows()
}

selected_label = st.sidebar.selectbox(
    "Company",
    list(company_options.keys())
)

selected_company = company_options[selected_label]

# percentile data

peer_data = load_percentiles(selected_group)

if peer_data.empty:
    st.warning("No percentile data available for this peer group.")
    st.stop()


# Latest year
peer_data["year_num"] = pd.to_numeric(
    peer_data["year"].astype(str).str.extract(r"(\d{4})")[0],
    errors="coerce"
)

latest_year = peer_data["year_num"].max()

if pd.isna(latest_year):
    st.warning("No valid year data available.")
    st.stop()

peer_data = peer_data[
    peer_data["year_num"] == latest_year
].copy()

st.caption(
    f"Peer Group: {selected_group} | Latest Year: {int(latest_year)}"
)

# 8 radar metrics

radar_metrics = [
    "roe",
    "roce",
    "net_profit_margin",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow",
    "interest_coverage",
]

metric_labels = {
    "roe": "ROE",
    "roce": "ROCE",
    "net_profit_margin": "NPM",
    "debt_to_equity": "D/E",
    "revenue_cagr_5yr": "Revenue CAGR 5Y",
    "pat_cagr_5yr": "PAT CAGR 5Y",
    "free_cash_flow": "FCF",
    "interest_coverage": "ICR",
}

# Keep only metrics available in database
available_metrics = peer_data["metric"].dropna().unique().tolist()

radar_metrics = [
    m for m in radar_metrics
    if m in available_metrics
]

# If database metric names differ, use first 8 available
if len(radar_metrics) < 8:
    radar_metrics = available_metrics[:8]

# Selected company percentile

company_radar = peer_data[
    (peer_data["company_id"] == selected_company)
    & (peer_data["metric"].isin(radar_metrics))
].copy()

company_radar = (
    company_radar
    .drop_duplicates("metric")
    .set_index("metric")
    .reindex(radar_metrics)
)

# Peer group average

peer_average = (
    peer_data[
        peer_data["metric"].isin(radar_metrics)
    ]
    .groupby("metric")["percentile_rank"]
    .mean()
    .reindex(radar_metrics)
)


company_values = (
    company_radar["percentile_rank"]
    .fillna(0)
    .tolist()
)

peer_values = (
    peer_average
    .fillna(0)
    .tolist()
)

# Close radar polygon
theta = [metric_labels[m] for m in radar_metrics]
theta = theta + [theta[0]]

company_plot = company_values + [company_values[0]]
peer_plot = peer_values + [peer_values[0]]

# radar chart

st.subheader("Company vs Peer Group Average")

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_plot,
        theta=theta,
        fill="toself",
        name=selected_company
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_plot,
        theta=theta,
        mode="lines",
        name="Peer Average",
        line=dict(dash="dash")
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]
        )
    ),
    showlegend=True,
    height=600
)

st.plotly_chart(
    fig,
    width="stretch"
)

# KPI comparison table

st.subheader("Peer KPI Comparison")

table_data = peer_data.pivot_table(
    index="company_id",
    columns="metric",
    values="value",
    aggfunc="first"
).reset_index()

table_data = table_data.merge(
    group_companies[
        ["company_id", "company_name", "is_benchmark"]
    ],
    on="company_id",
    how="left"
)

# Put identifying columns first
first_cols = [
    "company_id",
    "company_name",
    "is_benchmark"
]

metric_cols = [
    col for col in table_data.columns
    if col not in first_cols
]

# Correct column order
table_data = table_data[
    first_cols + metric_cols
].copy()


# Format KPI values for DISPLAY only
def format_kpi(value):
    if pd.isna(value):
        return "N/A"

    text = str(value).strip()

    if text.lower() in ["none", "nan", "<na>", ""]:
        return "N/A"

    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return text


display_table = table_data.copy()

# Only format KPI columns
for col in metric_cols:
    display_table[col] = display_table[col].apply(format_kpi)


# Benchmark flag as string
display_table["is_benchmark"] = (
    display_table["is_benchmark"].astype(str)
)


def highlight_benchmark(row):
    if row["is_benchmark"] in ["1", "1.0", "True"]:
        return [
            "background-color: #D4A017; "
            "color: #111111; "
            "font-weight: bold;"
        ] * len(row)

    return [""] * len(row)


styled_table = display_table.style.apply(
    highlight_benchmark,
    axis=1
)

st.dataframe(
    styled_table,
    width="stretch",
    hide_index=True
)

# Benchmark information
benchmark = group_companies[
    group_companies["is_benchmark"].isin([1, True, "1"])
]

if not benchmark.empty:
    benchmark_name = benchmark.iloc[0]["company_name"]
    benchmark_id = benchmark.iloc[0]["company_id"]

    st.markdown(
        f"""
        <div style="
            background-color:#D4A017;
            color:#111111;
            padding:14px 18px;
            border-radius:8px;
            font-weight:bold;
            font-size:16px;
            margin-top:15px;
        ">
        Benchmark Company: {benchmark_name} ({benchmark_id})
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("No benchmark company is assigned to this peer group.")