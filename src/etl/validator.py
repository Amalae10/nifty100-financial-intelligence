import pandas as pd
import requests

def check_pk(df, column):
    return df[column].duplicated().sum()

def check_company_year(df):
    return df.duplicated(["company_id","year"]).sum()

def check_fk(child, parent, column="company_id"):
    return (~child[column].isin(parent["id"])).sum()

def check_bs_balance(df):
    valid = df["total_assets"] != 0

    difference = (
        df.loc[valid, "total_assets"]
        - df.loc[valid, "total_liabilities"]
    ).abs()

    ratio = difference / df.loc[valid, "total_assets"]

    return (ratio >= 0.01).sum()

def check_opm(df):
    calculated = df["operating_profit"] / df["sales"] * 100
    return (abs(df["opm_percentage"] - calculated) > 1.0).sum()

def check_positive_sales(df):
    return (df["sales"] <= 0).sum()

def check_year_format(df):
    pattern = r"^\d{4}-\d{2}$"
    return (~df["year"].astype(str).str.match(pattern)).sum()

def check_ticker_format(df):
    tickers = df["company_id"].astype(str).str.strip().str.upper()
    return ((tickers.str.len() < 2) | (tickers.str.len() > 12)).sum()

def check_net_cash(df):
    total = (
        df["operating_activity"]
        + df["investing_activity"]
        + df["financing_activity"]
    )

    return (abs(df["net_cash_flow"] - total) > 10).sum()

def check_fixed_assets(df):
    return (df["fixed_assets"] < 0).sum()

def check_tax_range(df):
    return ((df["tax_percentage"] < 0) | (df["tax_percentage"] > 60)).sum()

def check_dividend_cap(df):
    return(df["dividend_payout"]> 200).sum()

def check_url(url):
    try:
        return requests.head(url, timeout=5).status_code != 200
    except requests.RequestException:
        return True

def check_eps_sign(df):
    return ((df["net_profit"] > 0) & (df["eps"] <= 0)).sum()

def check_strict_balance(df):
    return (df["total_liabilities"] != df["total_assets"]).sum()

def check_coverage(df):
    years = df.groupby("company_id")["year"].nunique()
    return (years < 5).sum()

