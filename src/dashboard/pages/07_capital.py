import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

st.title("Capital Allocation Map")


FILE_PATH = "output/capital_allocation.csv"


# load data
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(FILE_PATH)

    # Convert different formats:
    # Mar 2024 -> 2024
    # Mar-24   -> 2024
    def get_year(value):
        text = str(value)

        four_digit = pd.Series([text]).str.extract(r"(20\d{2})")[0].iloc[0]

        if pd.notna(four_digit):
            return int(four_digit)

        two_digit = pd.Series([text]).str.extract(r"-(\d{2})$")[0].iloc[0]

        if pd.notna(two_digit):
            return 2000 + int(two_digit)

        return None

    df["year_num"] = df["year"].apply(get_year)

    return df


df = load_data()


# year selector
years = sorted(
    df["year_num"].dropna().astype(int).unique(),
    reverse=True
)

selected_year = st.selectbox(
    "Select Year",
    years
)

year_df = df[
    df["year_num"] == selected_year
].copy()


# keep one record per company
year_df = year_df.drop_duplicates(
    subset=["company_id"],
    keep="last"
)

st.caption(
    f"{len(year_df)} companies available for {selected_year}"
)

if len(year_df) < 10:
    st.info(
        f"Limited data available for {selected_year}. "
        f"Only {len(year_df)} companies have data for this year."
    )
    
# Treemap
st.subheader("Capital Allocation Patterns")

year_df["value"] = 1

color_map = {
    "Shareholder Returns": "orange",
    "Reinvestor": "royalblue",
    "Mixed": "purple",
    "Liquidating Assets": "crimson",
    "Growth Funded by Debt": "green",
    "Distress Signal": "red",
    "Pre-Revenue": "gold",
    "Cash Accumulator": "deepskyblue"
}

fig = px.treemap(
    year_df,
    path=[
        px.Constant("Nifty 100"),
        "pattern_label",
        "company_id"
    ],
    values="value",
    color="pattern_label",
    color_discrete_map=color_map,
    hover_data={
        "company_id": True,
        "cfo_sign": True,
        "cfi_sign": True,
        "cff_sign": True,
        "value": False
    },
    title=f"Capital Allocation Map - {selected_year}"
)

fig.update_traces(
    textinfo="label+value",
    hovertemplate="<b>%{label}</b><extra></extra>"
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="white")
)

# Treemap click selection
clicked_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    key=f"capital_treemap_{selected_year}"
)

# Pattern drill down
st.subheader("Companies by Pattern")

patterns = sorted(
    year_df["pattern_label"]
    .dropna()
    .unique()
)


# default pattern

if (
    "capital_pattern" not in st.session_state
    or st.session_state.capital_pattern not in patterns
):
    st.session_state.capital_pattern = patterns[0]

# detect clicked treemap item

if clicked_points:
    point = clicked_points[0]

    curve_number = point.get("curveNumber", 0)
    point_number = point.get("pointNumber")

    if (
        point_number is not None
        and curve_number < len(fig.data)
    ):
        trace = fig.data[curve_number]

        if point_number < len(trace.labels):
            clicked_label = str(trace.labels[point_number])
            clicked_parent = str(trace.parents[point_number])

            if clicked_label in patterns:
                st.session_state.capital_pattern = clicked_label

            elif clicked_parent in patterns:
                st.session_state.capital_pattern = clicked_parent

selected_pattern = st.session_state.capital_pattern


st.write(
    f"### Selected Pattern: {selected_pattern}"
)


pattern_df = year_df[
    year_df["pattern_label"] == selected_pattern
][[
    "company_id",
    "cfo_sign",
    "cfi_sign",
    "cff_sign",
    "pattern_label"
]].copy()


st.write(
    f"**{len(pattern_df)} companies** in {selected_pattern}"
)

st.dataframe(
    pattern_df,
    width="stretch",
    hide_index=True
)


# csv download
csv = pattern_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Company List",
    csv,
    file_name=f"{selected_pattern}_{selected_year}.csv",
    mime="text/csv"
)