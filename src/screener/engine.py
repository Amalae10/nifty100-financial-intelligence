import sqlite3
import pandas as pd
import yaml

DB="nifty100.db"
CONFIG="config/screener_config.yaml"

def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data():
    with sqlite3.connect(DB) as conn:
        return pd.read_sql("""
            SELECT
                fr.*,
                s.broad_sector,
                p.sales,
                p.net_profit
            FROM financial_ratios fr
            JOIN sectors s
                ON fr.company_id = s.company_id
            LEFT JOIN profitandloss p
                ON fr.company_id = p.company_id
                AND fr.year = p.year
        """,conn)
    
def latest_data(df):
    df = df[df["year"] != "TTM"].copy()

    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    return (
        df.sort_values("year_num")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

def apply_filters(filters):
    df = latest_data(load_data())
    metrics = load_config()["metrics"]

    for rule, value in filters.items():
        col = metrics[rule]

        if rule == "de_eq":
            df = df[df[col] == value]

        elif rule == "de_max":
            df = df[df[col] < value]

        elif rule == "icr_min":
            df = df[df[col].isna() | (df[col] >= value)]

        elif rule.endswith("_min"):
            df = df[df[col] >= value]

        elif rule.endswith("_max"):
            df = df[df[col] <= value]

    return df.sort_values(
        "composite_quality_score",
        ascending=False
    )

def run_preset(name):
    config = load_config()
    filters = config["presets"][name]
    result = apply_filters(filters)

    if name == "turnaround_watch":
        all_data = load_data()
        all_data = all_data[all_data["year"] != "TTM"].copy()

        all_data["year_num"] = pd.to_numeric(
            all_data["year"].str.extract(r"(\d{4})")[0],
            errors="coerce"
        )

        all_data = all_data.sort_values(
            ["company_id", "year_num"]
        )

        all_data["previous_de"] = (
            all_data.groupby("company_id")["debt_to_equity"].shift(1)
        )

        latest = all_data.groupby("company_id").tail(1)

        valid = latest[
            (latest["free_cash_flow_cr"] > 0) &
            (latest["debt_to_equity"] < latest["previous_de"])
        ]["company_id"]

        result = result[result["company_id"].isin(valid)]

    return result

if __name__ == "__main__":
    presets = [
        "quality_compounder",
        "value_pick",
        "growth_accelerator",
        "dividend_champion",
        "debt_free_blue_chip",
        "turnaround_watch"
    ]

    for name in presets:
        result = run_preset(name)
        print(name, ":", len(result))