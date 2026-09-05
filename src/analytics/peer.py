import sqlite3
import pandas as pd

DB="nifty100.db"

METRICS={
    "roe":"return_on_equity_pct",
    "roce": "return_on_capital_pct",
    "net_profit_margin": "net_profit_margin_pct",
    "debt_to_equity": "debt_to_equity",
    "free_cash_flow": "free_cash_flow_cr",
    "pat_cagr_5yr": "pat_cagr_5yr",
    "revenue_cagr_5yr": "revenue_cagr_5yr",
    "eps_cagr_5yr": "eps_cagr_5yr",
    "interest_coverage": "interest_coverage",
    "asset_turnover": "asset_turnover",
}

def load_data():
    with sqlite3.connect(DB) as conn:
        ratios=pd.read_sql("SELECT * FROM financial_ratios",conn)
        peers=pd.read_sql("SELECT * FROM peer_groups",conn)

    return ratios,peers

def latest_ratios(df):
    df=df[df["year"] != "TTM"].copy()

    df["year_num"]=pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce")
    
    return(df.sort_values("year_num").groupby("company_id").tail(1).copy())

def percent_rank(series):
    n=series.notna().sum()

    if n<=1:
        return pd.Series(1.0,index=series.index)

    ranks=series.rank(method="min",na_option="keep")

    return (ranks -1)/(n-1)

def build_peer_percentiles():
    ratios,peers=load_data()
    ratios=latest_ratios(ratios)

    df=peers.merge(ratios,on="company_id",how="left")

    output=[]

    for group_name,group in df.groupby("peer_group_name"):
        for metric_name,col in METRICS.items():
            ranks=percent_rank(group[col])

            if metric_name=="debt_to_equity":
                ranks=1 - ranks

            temp=pd.DataFrame({
                "company_id": group["company_id"],
                "peer_group_name": group_name,
                "metric": metric_name,
                "value": group[col],
                "percentile_rank": ranks,
                "year": group["year"]
            })

            output.append(temp)

    return pd.concat(output,ignore_index=True)

def save_peer_percentiles():
    df=build_peer_percentiles()

    with sqlite3.connect(DB) as conn:
        df.to_sql("peer_percentiles",conn,if_exists="replace",index=False)

    print("peer_percentiles rows:",len(df))
    print("peer groups:",df["peer_group_name"].nunique())
    print("metrics:",df["metric"].nunique())

def get_company_peer(company_id):
    with sqlite3.connect(DB) as conn:
        peer = pd.read_sql(
            """
            SELECT peer_group_name
            FROM peer_groups
            WHERE company_id = ?
            """,
            conn,
            params=(company_id,)
        )

    if peer.empty:
        return "No peer group assigned"

    return peer.iloc[0]["peer_group_name"]

if __name__== "__main__":
    save_peer_percentiles