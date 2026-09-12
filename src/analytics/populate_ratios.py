import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm,
    roe,
    roce,
    roa,
    debt_to_equity,
    interest_coverage,
    asset_turnover,
    high_leverage
)

from src.analytics.composite_score import add_composite_score
from src.analytics.cagr import cagr
from src.analytics.cashflow_kpis import (
    fcf,
    cfo_pat_ratio,
    fcf_conversion
)
conn=sqlite3.connect("nifty100.db")

pl=pd.read_sql("SELECT * FROM profitandloss",conn)
bs=pd.read_sql("SELECT * FROM balancesheet",conn)
cf=pd.read_sql("SELECT * FROM cashflow",conn)
sectors = pd.read_sql("SELECT company_id, broad_sector FROM sectors",conn)
market = pd.read_sql("""SELECT company_id,year,market_cap_crore,enterprise_value_crore,pe_ratio,pb_ratio,ev_ebitda,dividend_yield_pct FROM market_cap""",conn)

# Merge core financial tables

df = pl.merge(bs,on=["company_id", "year"],how="left",suffixes=("_pl", "_bs"))

df = df.merge(cf,on=["company_id", "year"],how="left")

df = df.merge(sectors,on="company_id",how="left")

df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{4})$")[0],
    errors="coerce"
)

market["year_num"] = pd.to_numeric(
    market["year"].astype(str),
    errors="coerce"
)

df = df.merge(
    market.drop(columns=["year"]),
    on=["company_id", "year_num"],
    how="left"
)

# KPI's

# profitability

df["net_profit_margin_pct"]=df.apply(lambda r: net_profit_margin(r.net_profit,r.sales),axis=1)

df["operating_profit_margin_pct"]=df.apply(lambda r:operating_profit_margin(r.operating_profit,r.sales),axis=1)

df["ebit_margin_pct"] = df.apply(
    lambda r: None
    if r.sales == 0
    else ((r.operating_profit - r.depreciation) / r.sales) * 100,
    axis=1
)

df["return_on_equity_pct"]=df.apply(
    lambda r: roe(
        r.net_profit,
        r.equity_capital,
        r.reserves
    ),
    axis=1
)

df["return_on_capital_pct"] = df.apply(
    lambda r: roce(
        r.operating_profit - r.depreciation,
        r.equity_capital,
        r.reserves,
        r.borrowings
    ),
    axis=1
)

df["return_on_assets_pct"] = df.apply(
    lambda r: roa(
        r.net_profit,
        r.total_assets
    ),
    axis=1
)

# Leverage

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

df["high_leverage_flag"] = df.apply(
    lambda r: "High Leverage"
    if high_leverage(r.debt_to_equity, r.broad_sector)
    else "",
    axis=1
)

df["debt_free_flag"] = df["interest_coverage"].apply(
    lambda x: "Debt Free" if pd.isna(x) else ""
)

df["icr_warning_flag"] = df["interest_coverage"].apply(
    lambda x: "ICR Warning" if pd.notna(x) and x < 1.5 else ""
)

df["net_debt_cr"] = df["borrowings"] - df["investments"]

df["net_debt_to_ebitda"] = df.apply(
    lambda r: None
    if pd.isna(r.operating_profit) or r.operating_profit <= 0
    else r.net_debt_cr / r.operating_profit,
    axis=1
)

# Efficiency

df["asset_turnover"]=df.apply(
    lambda r: asset_turnover(
        r.sales,
        r.total_assets
    ),
    axis=1
)

df["fixed_asset_turnover"] = df.apply(
    lambda r: None if r.fixed_assets == 0
    else r.sales / r.fixed_assets,
    axis=1
)

df["working_capital_days"] = df.apply(
    lambda r: None if r.sales == 0
    else ((r.other_asset - r.other_liabilities) / r.sales) * 365,
    axis=1
)

df["inventory_turnover_proxy"] = df.apply(
    lambda r: None if r.fixed_assets == 0
    else r.sales / r.fixed_assets,
    axis=1
)

df["capex_intensity_pct"] = df.apply(
    lambda r: None
    if pd.isna(r.investing_activity) or r.sales == 0
    else abs(r.investing_activity) / r.sales * 100,
    axis=1
)

df["capex_intensity_label"] = df["capex_intensity_pct"].apply(
    lambda x: (
        None if pd.isna(x)
        else "Asset Light" if x < 3
        else "Moderate" if x <= 8
        else "Capital Intensive"
    )
)

# Cash quality

df["free_cash_flow_cr"] = df.apply(
    lambda r: None
    if pd.isna(r.operating_activity) or pd.isna(r.investing_activity)
    else fcf(r.operating_activity, r.investing_activity),
    axis=1
)

df["cfo_pat_ratio"] = df.apply(
    lambda r: None
    if pd.isna(r.operating_activity) or pd.isna(r.net_profit)
    else cfo_pat_ratio(r.operating_activity, r.net_profit),
    axis=1
)

# 5-year average CFO/PAT
df = df.sort_values(["company_id", "year_num"])

df["cfo_pat_5yr_avg"] = (
    df.groupby("company_id")["cfo_pat_ratio"]
    .transform(lambda x: x.rolling(5, min_periods=5).mean())
)

df["cfo_quality_score"] = df["cfo_pat_5yr_avg"].apply(
    lambda x: (
        "High Quality" if pd.notna(x) and x > 1
        else "Moderate" if pd.notna(x) and x >= 0.5
        else "Accrual Risk" if pd.notna(x)
        else "Insufficient Data"
    )
)

df["fcf_conversion_pct"] = df.apply(
    lambda r: None
    if pd.isna(r.free_cash_flow_cr) or pd.isna(r.operating_profit)
    else fcf_conversion(
        r.free_cash_flow_cr,
        r.operating_profit
    ),
    axis=1
)

df["capex_cr"] = df["investing_activity"].abs()

# Valuation
df["earnings_per_share"] = df["eps"]

df["book_value_per_share"]=(
    (df["equity_capital"] + df["reserves"])
    /df["equity_capital"].replace(0,pd.NA)
)

df["fcf_yield_pct"] = df.apply(
    lambda r: None
    if pd.isna(r.market_cap_crore) or r.market_cap_crore == 0
    else (r.free_cash_flow_cr / r.market_cap_crore) * 100,
    axis=1
)

# Other

df["dividend_payout_ratio_pct"] = df["dividend_payout"]
df["dividend_payout_warning"] = df["dividend_payout_ratio_pct"].apply(
    lambda x: "High Payout"
    if pd.notna(x) and x > 100
    else ""
)
df["total_debt_cr"]=df["borrowings"]
df["cash_from_operations_cr"]=df["operating_activity"]
df["opm_mismatch_flag"] = df.apply(
    lambda r: "Mismatch"
    if check_opm(r.operating_profit_margin_pct, r.opm_percentage)
    else "",
    axis=1
)

df["year_num"] = pd.to_numeric(
    df["year"].astype(str).str.extract(r"(\d{2,4})$")[0],
    errors="coerce"
)

df.loc[df["year_num"] < 100, "year_num"] += 2000

df = df.sort_values(["company_id", "year_num"])

# 3-year FCF concern flag

def fcf_concern(group):
    group = group.sort_values("year_num")
    flags = pd.Series(False, index=group.index)

    for i in range(2, len(group)):
        rows = group.iloc[i-2:i+1]

        years = rows["year_num"].tolist()
        fcfs = rows["free_cash_flow_cr"].tolist()

        consecutive = (
            years[1] == years[0] + 1
            and years[2] == years[1] + 1
        )

        if consecutive and all(x < 0 for x in fcfs):
            flags.loc[rows.index[-1]] = True

    return flags


df["fcf_concern_flag"] = False

for _, idx in df.groupby("company_id").groups.items():
    g = df.loc[idx]
    df.loc[g.index, "fcf_concern_flag"] = fcf_concern(g)


df["fcf_concern_flag"] = df["fcf_concern_flag"].map(
    {True: "FCF Concern", False: ""}
)

# 5-year CAGR

df = df.sort_values(["company_id", "year_num"])

def add_cagr(group, column, years):
    group = group.sort_values("year_num")

    values = {}
    flags = {}

    for i, row in group.iterrows():
        current_year = row["year_num"]

        old = group[group["year_num"] == current_year - years]

        if old.empty:
            values[i] = None
            flags[i] = "INSUFFICIENT"
            continue

        start = old.iloc[0][column]
        end = row[column]

        value, flag = cagr(start, end, years)

        values[i] = value
        flags[i] = flag

    return pd.Series(values), pd.Series(flags)

# Create 3Y, 5Y and 10Y CAGR
for source, name in [
    ("sales", "revenue"),
    ("net_profit", "pat"),
    ("eps", "eps"),
]:
    for years in [3, 5, 10]:

        value_col = f"{name}_cagr_{years}yr"
        flag_col = f"{value_col}_flag"

        df[value_col] = None
        df[flag_col] = "INSUFFICIENT"

        for _, idx in df.groupby("company_id").groups.items():
            g = df.loc[idx].sort_values("year_num")

            values, flags = add_cagr(g, source, years)

            df.loc[g.index, value_col] = values
            df.loc[g.index, flag_col] = flags

df["fcf_cagr_5yr"] = None
df["fcf_cagr_5yr_flag"] = "INSUFFICIENT"

for company_id, group in df.groupby("company_id"):
    group = group.sort_values("year_num")

    for i, row in group.iterrows():
        current_year = row["year_num"]

        old = group[group["year_num"] == current_year - 5]

        if old.empty:
            continue

        start = old.iloc[0]["free_cash_flow_cr"]
        end = row["free_cash_flow_cr"]

        value, flag = cagr(start, end, 5)

        df.loc[i, "fcf_cagr_5yr"] = value
        df.loc[i, "fcf_cagr_5yr_flag"] = flag

# Exclude TTM from CAGR
ttm = df["year"].astype(str).str.upper().eq("TTM")

for col in df.columns:
    if "_cagr_" in col:
        if col.endswith("_flag"):
            df.loc[ttm, col] = "INSUFFICIENT"
        else:
            df.loc[ttm, col] = None

# Composite Quality Score

df = add_composite_score(df)

print("Total rows before save:", len(df))
print("Composite populated:", df["composite_quality_score"].notna().sum())
print("Composite missing:", df["composite_quality_score"].isna().sum())

# save only required kpi columns

result = df[[
    "company_id",
    "year",

# PROFITABILITY
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "ebit_margin_pct",
    "return_on_equity_pct",
    "return_on_capital_pct",
    "return_on_assets_pct",

# LEVERAGE
    "debt_to_equity",
    "interest_coverage",
    "high_leverage_flag",
    "debt_free_flag",
    "icr_warning_flag",
    "net_debt_cr",
    "net_debt_to_ebitda",

# EFFICIENCY
    "asset_turnover",
    "fixed_asset_turnover",
    "working_capital_days",
    "inventory_turnover_proxy",

# CASH QUALITY
    "free_cash_flow_cr",
    "fcf_cagr_5yr",
    "fcf_cagr_5yr_flag",
    "cfo_pat_ratio",
    "cfo_pat_5yr_avg",
    "cfo_quality_score",
    "capex_intensity_pct",
    "capex_intensity_label",
    "fcf_conversion_pct",
    "fcf_concern_flag",
    "capex_cr",

# VALUATION
    "book_value_per_share",
    "earnings_per_share",
    "fcf_yield_pct",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct",

# GROWTH
    "revenue_cagr_3yr",
    "revenue_cagr_3yr_flag",
    "revenue_cagr_5yr",
    "revenue_cagr_5yr_flag",
    "revenue_cagr_10yr",
    "revenue_cagr_10yr_flag",

    "pat_cagr_3yr",
    "pat_cagr_3yr_flag",
    "pat_cagr_5yr",
    "pat_cagr_5yr_flag",
    "pat_cagr_10yr",
    "pat_cagr_10yr_flag",

    "eps_cagr_3yr",
    "eps_cagr_3yr_flag",
    "eps_cagr_5yr",
    "eps_cagr_5yr_flag",
    "eps_cagr_10yr",
    "eps_cagr_10yr_flag",


# OTHER
    "opm_mismatch_flag",
    "dividend_payout_warning",
    "composite_quality_score",
    "cash_from_operations_cr",
    "total_debt_cr",
    "dividend_payout_ratio_pct",
]]

result.to_sql("financial_ratios",conn,if_exists="replace",index=False)
conn.close()
print("financial_ratios populated:",len(result))