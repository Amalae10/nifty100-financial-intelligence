import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def get_companies():
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM companies",
            conn
        )


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    with get_connection() as conn:
        if year:
            return pd.read_sql(
                """
                SELECT *
                FROM financial_ratios
                WHERE company_id = ?
                AND year = ?
                """,
                conn,
                params=(ticker, year)
            )

        return pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year
            """,
            conn,
            params=(ticker,)
        )


@st.cache_data(ttl=600)
def get_pl(ticker):
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM profitandloss WHERE company_id = ?",
            conn,
            params=(ticker,)
        )


@st.cache_data(ttl=600)
def get_bs(ticker):
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM balancesheet WHERE company_id = ?",
            conn,
            params=(ticker,)
        )


@st.cache_data(ttl=600)
def get_cf(ticker):
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM cashflow WHERE company_id = ?",
            conn,
            params=(ticker,)
        )


@st.cache_data(ttl=600)
def get_sectors():
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM sectors",
            conn
        )


@st.cache_data(ttl=600)
def get_peers(group_name):
    with get_connection() as conn:
        return pd.read_sql(
            """
            SELECT *
            FROM peer_groups
            WHERE peer_group_name = ?
            """,
            conn,
            params=(group_name,)
        )


@st.cache_data(ttl=600)
def get_valuation(ticker):
    with get_connection() as conn:
        return pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            conn,
            params=(ticker,)
        )

@st.cache_data(ttl=600)
def get_ratios_by_year(year):
    with get_connection() as conn:
        return pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE year = ?
            """,
            conn,
            params=(year,)
        )


@st.cache_data(ttl=600)
def get_pros_cons(ticker):
    with get_connection() as conn:
        return pd.read_sql(
            """
            SELECT *
            FROM prosandcons
            WHERE company_id = ?
            """,
            conn,
            params=(ticker,)
        )