import pandas as pd
from pathlib import Path

OUT=Path("output")

def main():
    df=pd.read_csv(OUT/"capital_allocation.csv")

    # Normalize year
    df["year_num"]=pd.to_numeric(
        df["year"].astype(str).str.extract(r"(20\d{2}|\d{2})$")[0],
        errors="coerce",
    )
    df.loc[df["year_num"] < 100,"year_num"] +=2000

    # Remove same company-year duplicates
    df=df.drop_duplicates(
        ["company_id","year_num"],
        keep="last"
    )

    # Latest year distribution
    latest_year=int(df["year_num"].max())
    latest=df[df["year_num"]==latest_year]

    patterns = [
        "Reinvestor",
        "Shareholder Returns",
        "Liquidating Assets",
        "Distress Signal",
        "Growth Funded by Debt",
        "Cash Accumulator",
        "Pre-Revenue",
        "Mixed",
    ]

    distribution = (
        latest["pattern_label"]
        .value_counts()
        .reindex(patterns, fill_value=0)
        .rename_axis("pattern_label")
        .reset_index(name="company_count")
    )

    distribution.to_csv(OUT/"capital_allocation_distribution.csv",index=False)

    # Pattern changes year over year
    df=df.sort_values(["company_id","year_num"])

    df["previous_pattern"]=(df.groupby("company_id")["pattern_label"].shift(1))

    changes=df[
        df["previous_pattern"].notna() &
        (df["pattern_label"] != df["previous_pattern"])
    ].copy()

    changes=changes[
        [
            "company_id",
            "year_num",
            "previous_pattern",
            "pattern_label",
        ]
    ]

    changes=changes.rename(columns={
        "year_num":"year",
        "pattern_label":"current_pattern"
    })

    changes.to_csv(OUT/"pattern_changes.csv",index=False)

    print("Available company-years",len(df))
    print("Companies with CF data:", df["company_id"].nunique())
    print("Latest year:", latest_year)
    print("Latest-year companies:", latest["company_id"].nunique())

    print("\nLatest year distribution:")
    print(distribution.to_string(index=False))

    print("\nPattern changes:", len(changes))

    print("\nCreated:")
    print("output/capital_allocation_distribution.csv")
    print("output/pattern_changes.csv")


if __name__ == "__main__":
    main()

