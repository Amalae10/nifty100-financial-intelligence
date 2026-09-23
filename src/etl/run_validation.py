import pandas as pd
import re

from src.etl.loader import load_csv
from src.etl.validator import (
    check_pk,
    check_company_year,
    check_fk,
    check_bs_balance,
    check_opm,
    check_positive_sales,
    check_year_format,
    check_ticker_format,
    check_net_cash,
    check_fixed_assets,
    check_tax_range,
    check_dividend_cap,
    check_eps_sign,
    check_strict_balance,
    check_coverage,
)


# -------------------------
# Fix year format
# -------------------------

def fix_year(value):
    value = str(value).strip()

    if value.upper() == "TTM":
        return None

    # Plain year: 2013
    if value.isdigit() and len(value) == 4:
        return value + "-03"

    # Decimal year: 2024.5
    if value.endswith(".5") and value[:4].isdigit():
        return value[:4] + "-09"

    # Mar-13 / Mar 2013 / Mar 2023 15
    match = re.search(r"([A-Za-z]{3})[- ](\d{2,4})", value)

    if match:
        month, year = match.groups()

        if len(year) == 2:
            year = "20" + year

        date = pd.to_datetime(
            f"{month} {year}",
            format="%b %Y"
        )

        return date.strftime("%Y-%m")

    return None

# -------------------------
# Load CSV files
# -------------------------

companies = load_csv("data/raw/Companies.csv")
pl = load_csv("data/raw/Profit & Loss.csv")
bs = load_csv("data/raw/Balance Sheet.csv")
cf = load_csv("data/raw/Cash Flow.csv")


# -------------------------
# Clean company IDs
# -------------------------

companies["id"] = (
    companies["id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

for df in [pl, bs, cf]:

    df["company_id"] = (
        df["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

valid_ids = set(companies["id"])

pl = pl[pl["company_id"].isin(valid_ids)]
bs = bs[bs["company_id"].isin(valid_ids)]
cf = cf[cf["company_id"].isin(valid_ids)]

# -------------------------
# Remove TTM
# -------------------------

for df in [pl, bs, cf]:

    df.drop(
        df[
            df["year"]
            .astype(str)
            .str.strip()
            .str.upper()
            == "TTM"
        ].index,
        inplace=True
    )


# -------------------------
# Normalize years
# -------------------------

for df in [pl, bs, cf]:
    df["year"] = df["year"].apply(fix_year)


# -------------------------
# DQ-02 Fix duplicates
# Keep last occurrence
# -------------------------

pl = pl.drop_duplicates(
    ["company_id", "year"],
    keep="last"
)

bs = bs.drop_duplicates(
    ["company_id", "year"],
    keep="last"
)

cf = cf.drop_duplicates(
    ["company_id", "year"],
    keep="last"
)

cf["computed_net_cash_flow"] = (
    cf["operating_activity"]
    + cf["investing_activity"]
    + cf["financing_activity"]
)

cf["net_cash_mismatch"] = (
    (cf["net_cash_flow"] - cf["computed_net_cash_flow"]).abs() > 10
)

pl["computed_opm"] = (
    pl["operating_profit"] / pl["sales"] * 100
)

pl["opm_mismatch"] = (
    (pl["opm_percentage"] - pl["computed_opm"]).abs() >= 1
)

pl["valid_for_cagr"] = (
    (pl["sales"] > 0)
    & (
        pl.groupby("company_id")["year"]
        .transform("nunique") >= 3
    )
)

bs["valid_for_cagr"] = (
    bs.groupby("company_id")["year"]
    .transform("nunique") >= 3
)

cf["valid_for_cagr"] = (
    cf.groupby("company_id")["year"]
    .transform("nunique") >= 3
)

pl["dividend_payout_warning"] = (
    pl["dividend_payout"] > 200
)

pl["eps_sign_warning"] = (
    (pl["net_profit"] > 0)
    & (pl["eps"] <= 0)
)

def add_coverage_flag(df):
    counts = df.groupby("company_id")["year"].transform("nunique")

    df["coverage_warning"] = counts < 5
    df["valid_for_cagr"] = counts >= 3

    return df


pl = add_coverage_flag(pl)
bs = add_coverage_flag(bs)
cf = add_coverage_flag(cf)

# -------------------------
# Validation
# -------------------------

failures = []


# DQ-01
if check_pk(companies, "id") > 0:
    failures.append(
        ["DQ-01", "companies", "CRITICAL"]
    )


# DQ-02
for name, df in [
    ("profitandloss", pl),
    ("balancesheet", bs),
    ("cashflow", cf),
]:

    if check_company_year(df) > 0:
        failures.append(
            ["DQ-02", name, "CRITICAL"]
        )


# DQ-03
for name, df in [
    ("profitandloss", pl),
    ("balancesheet", bs),
    ("cashflow", cf),
]:

    if check_fk(
        df,
        companies,
        "company_id"
    ) > 0:

        failures.append(
            ["DQ-03", name, "CRITICAL"]
        )


# DQ-04
if check_bs_balance(bs) > 0:

    failures.append(
        ["DQ-04", "balancesheet", "WARNING"]
    )


# DQ-05
if check_opm(pl) > 0:

    failures.append(
        ["DQ-05", "profitandloss", "WARNING"]
    )


# DQ-06
if check_positive_sales(pl) > 0:

    failures.append(
        ["DQ-06", "profitandloss", "WARNING"]
    )


# DQ-07
for name, df in [
    ("profitandloss", pl),
    ("balancesheet", bs),
    ("cashflow", cf),
]:

    if check_year_format(df) > 0:

        failures.append(
            ["DQ-07", name, "CRITICAL"]
        )


# DQ-08
for name, df in [
    ("profitandloss", pl),
    ("balancesheet", bs),
    ("cashflow", cf),
]:

    if check_ticker_format(df) > 0:

        failures.append(
            ["DQ-08", name, "CRITICAL"]
        )


# DQ-09
if check_net_cash(cf) > 0:

    failures.append(
        ["DQ-09", "cashflow", "WARNING"]
    )


# DQ-10
if check_fixed_assets(bs) > 0:

    failures.append(
        ["DQ-10", "balancesheet", "WARNING"]
    )


# DQ-11
if check_tax_range(pl) > 0:

    failures.append(
        ["DQ-11", "profitandloss", "WARNING"]
    )


# DQ-12
if check_dividend_cap(pl) > 0:

    failures.append(
        ["DQ-12", "profitandloss", "WARNING"]
    )


# DQ-14
if check_eps_sign(pl) > 0:

    failures.append(
        ["DQ-14", "profitandloss", "WARNING"]
    )


# DQ-15
if check_strict_balance(bs) > 0:

    failures.append(
        ["DQ-15", "balancesheet", "INFO"]
    )


# DQ-16
for name, df in [
    ("profitandloss", pl),
    ("balancesheet", bs),
    ("cashflow", cf),
]:

    if check_coverage(df) > 0:

        failures.append(
            ["DQ-16", name, "WARNING"]
        )


# -------------------------
# Save validation report
# -------------------------

report = pd.DataFrame(failures, columns=["rule_id", "table", "severity"])

report = pd.DataFrame({
    "company_id": "ALL",
    "field": report["table"],
    "issue": report["rule_id"],
    "severity": report["severity"]
})

report.to_csv(
    "output/validation_failures.csv",
    index=False
)


# -------------------------
# Print result
# -------------------------

print("Validation completed")
print(report)