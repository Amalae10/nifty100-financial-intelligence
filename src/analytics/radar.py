import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DB="nifty100.db"
OUTPUT="reports/radar_charts"

Axes={
    "roe": "ROE",
    "roce": "ROCE",
    "net_profit_margin": "NPM",
    "debt_to_equity": "D/E",
    "free_cash_flow": "FCF",
    "pat_cagr_5yr": "PAT CAGR 5Y",
    "revenue_cagr_5yr": "Revenue CAGR 5Y",
}

def load_data():
    with sqlite3.connect(DB) as conn:
        peers=pd.read_sql(
            "SELECT * FROM peer_percentiles",
            conn
        )

        ratios=pd.read_sql(
            """
            SELECT company_id,year,composite_quality_score
            FROM financial_ratios""",
            conn
        )

        groups=pd.read_sql(
            "SELECT company_id,peer_group_name FROM peer_groups",
            conn
        )
    return peers,ratios,groups

def latest_ratios(df):
    df = df[df["year"] != "TTM"].copy()

    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    return(
        df.sort_values("year_num").groupby("company_id").tail(1).copy()
    )

def company_scores(company_id,peers,ratios):
    company=peers[
        peers["company_id"]==company_id
    ]

    scores=[]

    for metric in Axes:
        row=company[company["metric"]==metric]

        scores.append(
            row["percentile_rank"].iloc[0]
            if not row.empty else 0.5
        )

    comp=ratios[
        ratios["company_id"]==company_id
    ]["composite_quality_score"]

    comp_score=(
        comp.iloc[0]/100
        if not comp.empty and pd.notna(comp.iloc[0])
        else 0.5
    )

    scores.append(comp_score)

    return scores

def peer_average(group_name,peers,ratios):
    companies=peers[
        peers["peer_group_name"]==group_name
    ]["company_id"].unique()

    values=[
        company_scores(c,peers,ratios)
        for c in companies
    ]

    return np.nanmean(values,axis=0)

def create_radar(company_id,group_name,peers,ratios):
    values =company_scores(
        company_id,peers,ratios
    )

    average=peer_average(
        group_name,peers,ratios
    )

    labels=list(Axes.values())+["Composite"]

    angles=np.linspace(
        0,2*np.pi,len(labels),
        endpoint=False
    ).tolist()

    values += values[:1]
    average = list(average) + [average[0]]
    angles += angles[:1]

    fig,ax =plt.subplots(
        figsize=(8,8),
        subplot_kw={"polar":True}
    )

    ax.plot(angles,values,linewidth=2,label=company_id)

    ax.fill(angles,values,alpha=0.25)

    ax.plot(angles,average,linestyle="--",linewidth=2,label="peer Average")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        labels,
        fontsize=10
    )

    ax.set_ylim(0,1)

    ax.set_title(
        f"{company_id} - {group_name}",
        fontsize=14,
        pad=20
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.25, 1.10)
    )

    plt.tight_layout()

    path=os.path.join(OUTPUT,f"{company_id}_radar.png")

    plt.savefig(path,dpi=150,bbox_inches="tight")
    plt.close()

def standalone_chart(company_id, ratios):
    row = ratios[ratios["company_id"] == company_id].copy()

    if row.empty:
        return

    # Try composite first
    valid = row.dropna(subset=["composite_quality_score"])

    if not valid.empty:
        company_value = valid["composite_quality_score"].iloc[-1]
        nifty_avg = ratios["composite_quality_score"].mean()
        metric_name = "Composite Quality Score"
        ylim = (0, 100)

    else:
        # Fallback to ROE
        with sqlite3.connect(DB) as conn:
            full = pd.read_sql(
                """
                SELECT company_id, year, return_on_equity_pct
                FROM financial_ratios
                """,
                conn
            )

        company_data = full[
            full["company_id"] == company_id
        ].dropna(subset=["return_on_equity_pct"])

        if company_data.empty:
            print(f"{company_id}: No usable standalone metric")
            return

        company_value = (
            company_data["return_on_equity_pct"].iloc[-1]
        )

        nifty_avg = (
            full["return_on_equity_pct"].mean()
        )

        metric_name = "ROE (%)"

        max_value = max(company_value, nifty_avg)
        ylim = (0, max_value * 1.25)

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        [company_id, "Nifty 100 Avg"],
        [company_value, nifty_avg]
    )

    ax.set_ylabel(metric_name, fontsize=11)
    ax.set_ylim(*ylim)

    ax.set_title(
        f"{company_id} - Standalone Comparison",
        fontsize=14
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT,
            f"{company_id}_radar.png"
        ),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

def generate_all():
    os.makedirs(OUTPUT, exist_ok=True)

    peers, ratios, groups = load_data()

    full_ratios = ratios.copy()
    latest = latest_ratios(ratios)

    all_companies = latest["company_id"].unique()

    for company_id in all_companies:

        row = groups[
            groups["company_id"] == company_id
        ]

        if row.empty:
            standalone_chart(
                company_id,
                full_ratios
            )

        else:
            group_name = row[
                "peer_group_name"
            ].iloc[0]

            create_radar(
                company_id,
                group_name,
                peers,
                latest
            )

    print(
        "Radar charts created:",
        len(all_companies)
    )


if __name__ == "__main__":
    generate_all()
    
