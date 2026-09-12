import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_ratios_by_year,
    get_sectors
)

import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_ratios_by_year,
    get_sectors
)

st.title("Nifty 100 Analytics")

# year selector

year_num=st.sidebar.selectbox(
    "Select Year",
    list(range(2024,2018,-1))
)

year=f"Mar {year_num}"

ratios=get_ratios_by_year(year)
companies=get_companies()
sectors=get_sectors()

# kpi cards
if ratios.empty:
    st.warning(f"No data available for {year}")
    st.stop()

avg_roe=ratios["return_on_equity_pct"].mean()
median_pe=ratios["pe_ratio"].median()
median_de = ratios["debt_to_equity"].median()
median_growth=ratios["revenue_cagr_5yr"].median()

debt_free=(ratios["debt_free_flag"].fillna(0).astype(bool).sum())

c1,c2,c3,c4,c5,c6=st.columns(6)

c1.metric("Average ROE", f"{avg_roe:.2f}%")
c2.metric("Median P/E",f"{median_pe:.2f}")
c3.metric("Median D/E", f"{median_de:.2f}")
c4.metric("Total Companies",len(companies))
c5.metric("Median Revenue CAGR 5Y",f"{median_growth:.2f}%")
c6.metric("Debt-Free Companies",int(debt_free))

st.divider()

# Sector Donut

st.subheader("Sector Breakdown")

available=ratios[["company_id"]].drop_duplicates()

sector_data=sectors.merge(available,on="company_id",how="inner")

sector_count=(sector_data.groupby("broad_sector").size().reset_index(name="Companies"))

fig=px.pie(sector_count,names="broad_sector",values="Companies",hole=0.5,title=f"Sector Distribution - {year_num}")

st.plotly_chart(fig,width="stretch")

# Top 5

st.subheader("Top 5 Companies by Composite Quality Score")

top5 = (
    ratios[["company_id", "composite_quality_score"]]
    .dropna(subset=["composite_quality_score"])
    .sort_values("composite_quality_score", ascending=False)
    .head(5)
)

top5=top5.merge(
    companies[["id","company_name"]],
    left_on="company_id",
    right_on="id",
    how="left")

top5=top5[["company_id","company_name","composite_quality_score"]]

top5.columns=["Ticker","Company","Composite Score"]

st.dataframe(
    top5,width="stretch",
    hide_index=True
)