import pandas as pd

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]


def main():

    df = pd.read_csv("output/clustering_features.csv")

    profile = (
        df.groupby("cluster_id")[FEATURES]
        .agg(["mean", "median"])
        .round(2)
    )

    profile.to_csv("output/cluster_profiles.csv")

    print("\nCLUSTER PROFILES")
    print(profile.to_string())

    print("\nCOMPANIES IN EACH CLUSTER")

    for cluster_id in sorted(df["cluster_id"].unique()):

        companies = df.loc[
            df["cluster_id"] == cluster_id,
            "company_id"
        ].tolist()

        print(f"\nCluster {cluster_id}:")
        print(", ".join(companies))


if __name__ == "__main__":
    main()