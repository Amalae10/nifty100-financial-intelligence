import sqlite3
from pathlib import Path
import pandas as pd

DB = "nifty100.db"
OUT = Path("output")
OUT.mkdir(exist_ok=True)

KEYWORDS = {
    "Financials": [
        "bank", "banking", "finance", "financial",
        "insurance", "lending", "loan", "credit"
    ],
    "Information Technology": [
        "software", "technology", "digital",
        "information technology", "it services"
    ],
    "Healthcare": [
        "pharma", "pharmaceutical", "healthcare",
        "medicine", "hospital", "drug"
    ],
    "Energy": [
        "oil", "gas", "petroleum", "energy",
        "refinery", "refining"
    ],
    "Automobile": [
        "automobile", "automotive", "vehicle",
        "motorcycle", "car", "tractor"
    ],
    "FMCG": [
        "consumer goods", "food", "beverage",
        "personal care", "household"
    ],
    "Metals": [
        "steel", "metal", "aluminium",
        "mining", "iron"
    ],
    "Power": [
        "power", "electricity", "electric",
        "utility", "utilities"
    ],
    "Cement": [
        "cement", "concrete"
    ],
    "Telecom": [
        "telecom", "telecommunication",
        "mobile network"
    ],
    "Consumer": [
        "retail", "consumer", "jewellery",
        "fashion", "apparel"
    ],
}


def classify(text):
    text = str(text).lower()

    scores = {
        sector: sum(keyword in text for keyword in words)
        for sector, words in KEYWORDS.items()
    }

    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else "Unclassified"


def main():
    with sqlite3.connect(DB) as conn:
        companies = pd.read_sql("""
            SELECT id AS company_id,
                   company_name,
                   about_company
            FROM companies
        """, conn)

        sectors = pd.read_sql("""
            SELECT company_id, broad_sector
            FROM sectors
        """, conn)

    df = companies.merge(sectors, on="company_id", how="left")

    df["generated_tag"] = df["about_company"].apply(classify)

    df["match"] = (
        df["generated_tag"].str.lower()
        == df["broad_sector"].fillna("").str.lower()
    )

    df.to_csv(
        OUT / "business_description_tags.csv",
        index=False
    )

    print("Companies:", len(df))
    print("Classified:", (df["generated_tag"] != "Unclassified").sum())
    print("Unclassified:", (df["generated_tag"] == "Unclassified").sum())
    print("Exact sector matches:", df["match"].sum())
    print("\nCreated:")
    print("output/business_description_tags.csv")


if __name__ == "__main__":
    main()