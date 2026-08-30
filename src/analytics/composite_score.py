import pandas as pd


def scale(series):
    low = series.quantile(0.10)
    high = series.quantile(0.90)

    if pd.isna(low) or pd.isna(high) or high == low:
        return pd.Series(50, index=series.index)

    clipped = series.clip(low, high)
    return ((clipped - low) / (high - low)) * 100


def de_score(x):
    if pd.isna(x):
        return None
    if x <= 0:
        return 100
    if x <= 0.5:
        return 85
    if x <= 1:
        return 70
    if x <= 2:
        return 50
    if x > 5:
        return 0
    return 25


def icr_score(x):
    if pd.isna(x):
        return 100
    if x > 10:
        return 100
    if x >= 5:
        return 75
    if x >= 3:
        return 50
    if x < 1.5:
        return 0
    return 25


def add_composite_score(df):
    df = df.copy()

    roe_s = scale(df["return_on_equity_pct"])
    roce_s = scale(df["return_on_capital_pct"])
    npm_s = scale(df["net_profit_margin_pct"])

    revenue_s = scale(df["revenue_cagr_5yr"])
    pat_s = scale(df["pat_cagr_5yr"])
    fcf_s = scale(df["fcf_cagr_5yr"])

    cfo_s = scale(df["cfo_pat_ratio"])
    de_s = df["debt_to_equity"].apply(de_score)
    icr_s = df["interest_coverage"].apply(icr_score)

    fcf_positive = (df["free_cash_flow_cr"] > 0).astype(int) * 100

    score = (
        roe_s * 0.15
        + roce_s * 0.10
        + npm_s * 0.10
        + fcf_s * 0.15
        + cfo_s * 0.10
        + fcf_positive * 0.05
        + revenue_s * 0.10
        + pat_s * 0.10
        + de_s * 0.10
        + icr_s * 0.05
    )

    df["composite_quality_score"] = score.clip(0, 100)

    return df