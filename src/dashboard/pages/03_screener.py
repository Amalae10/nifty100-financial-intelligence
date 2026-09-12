import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sqlite3
import pandas as pd
import streamlit as st

DB_PATH="nifty100.db"
st.title("Financial Screener")

st.markdown("""
<style>
div.stButton > button {
    white-space: nowrap;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT
                fr.company_id,
                c.company_name,
                s.broad_sector AS sector,
                fr.return_on_equity_pct AS roe,
                fr.debt_to_equity AS de,
                fr.free_cash_flow_cr AS fcf,
                fr.revenue_cagr_5yr AS revenue_cagr,
                fr.pat_cagr_5yr AS pat_cagr,
                fr.operating_profit_margin_pct AS opm,
                fr.pe_ratio AS pe,
                fr.pb_ratio AS pb,
                fr.dividend_yield_pct AS dividend_yield,
                fr.interest_coverage AS icr,
                fr.composite_quality_score AS composite_score
            FROM financial_ratios fr
            LEFT JOIN companies c
                ON fr.company_id = c.id
            LEFT JOIN sectors s
                ON fr.company_id = s.company_id
            WHERE fr.year = 'Mar 2024'
        """, conn)

df=load_data()

# Preset values

presets = {
    "Quality": {
        "roe": 15.0, "de": 1.0, "fcf": 0.0,
        "revenue": 10.0, "pat": -100.0, "opm": -100.0,
        "pe": 500.0, "pb": 100.0,
        "dividend": 0.0, "icr": -100.0
    },

    "Value": {
        "roe": 0.0, "de": 2.0, "fcf": -100000.0,
        "revenue": -100.0, "pat": -100.0, "opm": -100.0,
        "pe": 25.0, "pb": 4.0,
        "dividend": 1.0, "icr": -100.0
    },

    "Growth": {
        "roe": 0.0, "de": 2.0, "fcf": -100000.0,
        "revenue": 15.0, "pat": 20.0, "opm": -100.0,
        "pe": 500.0, "pb": 100.0,
        "dividend": 0.0, "icr": -100.0
    },

    "Dividend": {
        "roe": 0.0, "de": 10.0, "fcf": 0.0,
        "revenue": -100.0, "pat": -100.0, "opm": -100.0,
        "pe": 500.0, "pb": 100.0,
        "dividend": 2.0, "icr": -100.0
    },

    "Debt-Free": {
        "roe": 10.0, "de": 0.2, "fcf": -100000.0,
        "revenue": -100.0, "pat": -100.0, "opm": -100.0,
        "pe": 500.0, "pb": 100.0,
        "dividend": 0.0, "icr": -100.0
    },

    "Turnaround": {
        "roe": 0.0, "de": 10.0, "fcf": 0.0,
        "revenue": 10.0, "pat": -100.0, "opm": -100.0,
        "pe": 500.0, "pb": 100.0,
        "dividend": 0.0, "icr": -100.0
    }
}
# default slider values

defaults = {
    "roe": -100.0,
    "de": 10.0,
    "fcf": -100000.0,
    "revenue": -100.0,
    "pat": -100.0,
    "opm": -100.0,
    "pe": 500.0,
    "pb": 100.0,
    "dividend": 0.0,
    "icr": -100.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# 6 PRESET BUTTONS
# -----------------------------

st.sidebar.subheader("Preset Screens")

if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = None

def apply_preset(name):
    st.session_state.selected_preset = name

    for key, value in presets[name].items():
        st.session_state[key] = value


c1, c2 = st.sidebar.columns(2)

c1.button(
    "Quality",
    on_click=apply_preset,
    args=("Quality",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Quality" else "secondary"
)

c2.button(
    "Value",
    on_click=apply_preset,
    args=("Value",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Value" else "secondary"
)

c1, c2 = st.sidebar.columns(2)

c1.button(
    "Growth",
    on_click=apply_preset,
    args=("Growth",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Growth" else "secondary"
)

c2.button(
    "Dividend",
    on_click=apply_preset,
    args=("Dividend",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Dividend" else "secondary"
)

c1, c2 = st.sidebar.columns(2)

c1.button(
    "Debt-Free",
    on_click=apply_preset,
    args=("Debt-Free",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Debt-Free" else "secondary"
)

c2.button(
    "Turnaround",
    on_click=apply_preset,
    args=("Turnaround",),
    use_container_width=True,
    type="primary" if st.session_state.selected_preset == "Turnaround" else "secondary"
)

# -----------------------------
# 10 FILTER SLIDERS
# -----------------------------

st.sidebar.subheader("Filters")

roe_min = st.sidebar.slider(
    "ROE Min (%)",
    -100.0,
    200.0,
    key="roe",
    step=1.0
)

de_max = st.sidebar.slider(
    "D/E Max",
    0.0,
    10.0,
    key="de",
    step=0.1
)

fcf_min = st.sidebar.slider(
    "FCF Min (₹ Cr)",
    -100000.0,
    100000.0,
    key="fcf",
    step=500.0
)

revenue_min = st.sidebar.slider(
    "Revenue CAGR Min (%)",
    -100.0,
    100.0,
    key="revenue",
    step=1.0
)

pat_min = st.sidebar.slider(
    "PAT CAGR Min (%)",
    -100.0,
    100.0,
    key="pat",
    step=1.0
)

opm_min = st.sidebar.slider(
    "OPM Min (%)",
    -100.0,
    100.0,
    key="opm",
    step=1.0
)

pe_max = st.sidebar.slider(
    "P/E Max",
    0.0,
    500.0,
    key="pe",
    step=1.0
)

pb_max = st.sidebar.slider(
    "P/B Max",
    0.0,
    100.0,
    key="pb",
    step=0.5
)

dividend_min = st.sidebar.slider(
    "Dividend Yield Min (%)",
    0.0,
    20.0,
    key="dividend",
    step=0.1
)

icr_min = st.sidebar.slider(
    "ICR Min",
    -100.0,
    100.0,
    key="icr",
    step=0.5
)
# apply filters

mask = pd.Series(True, index=df.index)

# Apply a filter only when slider is actually restrictive

if roe_min > -100:
    mask &= df["roe"].notna() & (df["roe"] >= roe_min)

if de_max < 10:
    mask &= df["de"].notna() & (df["de"] <= de_max)

if fcf_min > -100000:
    mask &= df["fcf"].notna() & (df["fcf"] >= fcf_min)

if revenue_min > -100:
    mask &= (
        df["revenue_cagr"].notna()
        & (df["revenue_cagr"] >= revenue_min)
    )

if pat_min > -100:
    mask &= (
        df["pat_cagr"].notna()
        & (df["pat_cagr"] >= pat_min)
    )

if opm_min > -100:
    mask &= df["opm"].notna() & (df["opm"] >= opm_min)

if pe_max < 500:
    mask &= df["pe"].notna() & (df["pe"] <= pe_max)

if pb_max < 100:
    mask &= df["pb"].notna() & (df["pb"] <= pb_max)

if dividend_min > 0:
    mask &= (
        df["dividend_yield"].notna()
        & (df["dividend_yield"] >= dividend_min)
    )

if icr_min > -100:
    mask &= (
        df["icr"].isna()
        | (df["icr"] >= icr_min)
    )

filtered = df[mask].copy()

filtered = filtered.sort_values(
    "composite_score",
    ascending=False,
    na_position="last"
)

# Results

st.subheader(f"{len(filtered)} companies match your filters")

visible=filtered.rename(
    columns={
        "company_id": "Ticker",
        "company_name": "Company",
        "sector": "Sector",
        "composite_score": "Composite Score",
        "roe": "ROE %",
        "de": "D/E",
        "fcf": "FCF ₹Cr",
        "revenue_cagr": "Revenue CAGR 5Y %",
        "pat_cagr": "PAT CAGR 5Y %",
        "opm": "OPM %",
        "pe": "P/E",
        "pb": "P/B",
        "dividend_yield": "Dividend Yield %",
        "icr": "ICR"
    }
)
display_df = visible.copy()

def format_value(x):
    if pd.isna(x) or str(x).strip().lower() in ["none", "nan", "<na>", ""]:
        return "N/A"

    if isinstance(x, (int, float)):
        return f"{x:.2f}"

    return str(x)

display_df = display_df.map(format_value)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)

csv = visible.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="screener_results.csv",
    mime="text/csv"
)