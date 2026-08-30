import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    roe,
    debt_to_equity,
    interest_coverage,
    asset_turnover
)

from src.analytics.cagr import cagr
from src.analytics.cashflow_kpis import fcf

conn=sqlite3.connect("nifty100.db")

pl=pd.read_sql("SELECT * FROM profitandloss",conn)
bs=pd.read_sql("SELECT * FROM balancesheet",conn)
cf=pd.read_sql("SELECT * FROM cashflow",conn)

# Merge core financial tables

df = pl.merge(bs,on=["company_id", "year"],how="left",suffixes=("_pl", "_bs"))

df = df.merge(cf,on=["company_id", "year"],how="left")

# KPI's

df["net_profit_margin_pct"]=df.apply(lambda r: net_profit_margin(r.net_profit,r.sales),axis=1)

df["operating_profit_margin_pct"]=df.apply(lambda r:operating_profit_margin(r.operating_profit,r.sales),axis=1)

df["return_on_equity_pct"]=df.apply(
    lambda r: roe(
        r.net_profit,
        r.equity_capital,
        r.reserves
    ),
    axis=1
)

df["debt_to_equity"]=df.apply(
    lambda r: debt_to_equity(
        r.borrowings,
        r.equity_capital,
        r.reserves
    ),axis=1)

df["interest_coverage"]=df.apply(
    lambda r:interest_coverage(
        r.operating_profit,
        r.other_income,
        r.interest
    ),axis=1
)

df["asset_turnover"]=df.apply(
    lambda r: asset_turnover(
        r.sales,
        r.total_assets
    ),
    axis=1
)

df["free_cash_flow_cr"] = df.apply(
    lambda r: None
    if pd.isna(r.operating_activity) or pd.isna(r.investing_activity)
    else fcf(r.operating_activity, r.investing_activity),
    axis=1
)

df["capex_cr"] = df["investing_activity"].abs()
df["earnings_per_share"] = df["eps"]

df["book_value_per_share"]=(
    (df["equity_capital"] + df["reserves"])
    /df["equity_capital"].replace(0,pd.NA)
)

df["dividend_payout_ratio_pct"] = df["dividend_payout"]
df["total_debt_cr"]=df["borrowings"]
df["cash_from_operations_cr"]=df["operating_activity"]

df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{2,4})$")[0],
    errors="coerce"
)

df.loc[df["year_num"] < 100, "year_num"] += 2000

df = df.sort_values(["company_id", "year_num"])

# 5-year CAGR

df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{2,4})$")[0],
    errors="coerce"
)

df.loc[df["year_num"] < 100, "year_num"] += 2000

df = df.sort_values(["company_id", "year_num"])

def get_cagr(group, column):
    values = group[column].tolist()
    result = []

    for i in range(len(values)):
        if i < 5:
            result.append(None)
        else:
            value, flag = cagr(values[i - 5], values[i], 5)
            result.append(value)

    return pd.Series(result, index=group.index)


df["revenue_cagr_5yr"] = (
    df.groupby("company_id", group_keys=False)
      .apply(lambda g: get_cagr(g, "sales"), include_groups=False)
)

df["pat_cagr_5yr"] = (
    df.groupby("company_id", group_keys=False)
      .apply(lambda g: get_cagr(g, "net_profit"), include_groups=False)
)

df["eps_cagr_5yr"] = (
    df.groupby("company_id", group_keys=False)
      .apply(lambda g: get_cagr(g, "eps"), include_groups=False)
)

# Exclude TTM from CAGR
ttm = df["year"].astype(str).str.upper().eq("TTM")

df.loc[ttm, [
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr"
]] = None

# Composite Quality Score
score = (
    df["return_on_equity_pct"].clip(0, 30) / 30 * 40
    + df["net_profit_margin_pct"].clip(0, 20) / 20 * 30
    + (1 - df["debt_to_equity"].clip(0, 5) / 5) * 20
    + (df["free_cash_flow_cr"] > 0).astype(int) * 10
)

df["composite_quality_score"] = score.clip(0, 100)

# save only required kpi columns

result=df[[
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "capex_cr",
    "earnings_per_share",
    "book_value_per_share",
    "dividend_payout_ratio_pct",
    "total_debt_cr",
    "cash_from_operations_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "composite_quality_score"
]]

result.to_sql("financial_ratios",conn,if_exists="replace",index=False)
conn.close()
print("financial_ratios populated:",len(result))