import os
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DB="nifty100.db"

FEATURES=[
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]

def main():
    conn=sqlite3.connect(DB)

    # Latest ratio row for each company
    ratios=pd.read_sql("""
        SELECT *
        FROM financial_ratios
    """,conn)

    sectors=pd.read_sql("""
        SELECT company_id,broad_sector
        FROM sectors
    """,conn)
    conn.close()

    # Keep latest year per company
    ratios["year_num"] = pd.to_numeric(
        ratios["year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    # Exclude TTM / rows without a valid year
    ratios = ratios.dropna(subset=["year_num"])

    # Keep latest financial year for each company
    ratios = (
        ratios.sort_values(["company_id", "year_num"])
        .groupby("company_id")
        .tail(1)
    )

    df=ratios[["company_id"] + FEATURES].merge(
        sectors,on="company_id",how="left"
    )

    # converts feacturs to numeric
    df[FEATURES]=df[FEATURES].apply(pd.to_numeric,errors="coerce")

    print("\nBEFORE IMPUTATION:")

    print(
        df.loc[
            df["company_id"].isin(
                ["TCS", "INFY", "RELIANCE", "HDFCBANK", "SBIN"]
            ),
            ["company_id"] + FEATURES
        ].to_string(index=False)
    )

    # Sector median imputation
    for col in FEATURES:
        df[col]=df[col].fillna(
            df.groupby("broad_sector")[col].transform("median")
        )

        # Fallback if entire sector is missing
        df[col]=df[col].fillna(df[col].median())

    # scaling
    scaler=StandardScaler()
    X=scaler.fit_transform(df[FEATURES])

    # ELbow plot k=2 to 10
    inertias=[]
    for k in range(2,11):
        model=KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )
        model.fit(X)
        inertias.append(model.inertia_)

    os.makedirs("reports",exist_ok=True)

    plt.figure(figsize=(7,5))
    plt.plot(range(2,11),inertias,marker="o")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow plot")
    plt.tight_layout()
    plt.savefig("reports/elbow_plot.png",dpi=150)
    plt.close()

    # Final KMeans
    model=KMeans(n_clusters=5,random_state=42,n_init=10)

    df["cluster_id"]=model.fit_predict(X)
    distances=model.transform(X)

    df["distance_from_centroid"]=[
        distances[i,cluster]
        for i,cluster in enumerate(df["cluster_id"])
    ]

    # Temporary names - reviwed properly on Day 37
    CLUSTER_NAMES = {
        0: "Core Quality Companies",
        1: "High-Margin Compounders",
        2: "High-ROE Outliers",
        3: "Leveraged Growth Financials",
        4: "High-FCF Growth Outlier"
    }

    df["cluster_name"] = df["cluster_id"].map(CLUSTER_NAMES)

    feature_output = df[
        ["company_id", "broad_sector", "cluster_id"] + FEATURES
    ].copy()

    feature_output.to_csv(
        "output/clustering_features.csv",
        index=False
    )

    output=df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid"

        ]
    ].sort_values("company_id")

    os.makedirs("output",exist_ok=True)

    output.to_csv("output/cluster_labels.csv",index=False)

    print("companies clustered:",len(output))
    print("\nCluster distribution:")
    print(output["cluster_id"].value_counts().sort_index())

    print("\nCreated:")
    print("output/clustering_features.csv")
    print("reports/elbow_plot.png")
    print("output/cluster_labels.csv")

if __name__ == "__main__":
    main()
