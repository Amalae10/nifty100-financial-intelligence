import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import sqlite3
import requests
import pandas as pd
import streamlit as st

DB_PATH=ROOT/"nifty100.db"

st.title("Annual Reports")

# Load companies

@st.cache_data(ttl=600)
def load_companies():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT id AS company_id,company_name
            FROM companies
            ORDER BY company_name
        """,conn)

# load reports

@st.cache_data(ttl=600)
def load_reports(company_id):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("""
            SELECT year,annual_report
            FROM documents
            WHERE company_id=?
            ORDER BY CAST(year AS INTEGER) DESC
        """,conn,params=(company_id,))

# check report url

@st.cache_data(ttl=600)
def check_url(url):
    if not url or pd.isna(url):
        return False

    try:
        response=requests.head(
            url,
            timeout=5,
            allow_redirects=True
        )

        #some servers block HEAD requests
        if response.status_code==405:
            response=requests.get(
                url,
                timeout=5,
                stream=True
            )

        return response.status_code !=404

    except requests.RequestException:
        return False

companies=load_companies()

company_option=(
    companies["company_id"]
    + " - "
    + companies["company_name"]
)

selected_company=st.selectbox(
    "Search Company",
    company_option
)

company_id=selected_company.split(" - ",1)[0]

reports=load_reports(company_id)

# Display reports

if reports.empty:
    st.warning(
        "No annual reports available for this company."
    )

else:
    st.subheader(
        f"Available Annual Reports - {company_id}"    
    )

    for _,row in reports.iterrows():

        year=row["year"]
        url=row["annual_report"]

        col1,col2=st.columns([1,3])

        with col1:
            st.write(f"**{year}**")

        with col2:
            if check_url(url):
                st.link_button(
                    "Open BSE PDF",
                    url
                )
            else:
                st.markdown(
                    """
                    <span style=
                    "background-color:#dc3545;
                     color:white;
                     padding:6px 12px;
                     border-radius:6px;
                     font-weight:bold;
                ">
                Report unavailable
                </span>""",
                unsafe_allow_html=True)
