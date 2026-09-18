from pathlib import Path
import pandas as pd
import nltk

from nltk.sentiment import SentimentIntensityAnalyzer

OUT = Path("output")

nltk.download("vader_lexicon", quiet=True)

sia = SentimentIntensityAnalyzer()


def main():
    path = OUT / "pros_cons_generated.csv"

    df = pd.read_csv(path)

    df["sentiment_score"] = df["text"].apply(
        lambda x: sia.polarity_scores(str(x))["compound"]
    )

    df["sentiment_label"] = df["sentiment_score"].apply(
        lambda x: "Positive"
        if x > 0.05
        else "Negative"
        if x < -0.05
        else "Neutral"
    )

    df.to_csv(
        OUT / "pros_cons_sentiment.csv",
        index=False
    )

    print("Rows:", len(df))
    print("\nSentiment counts:")
    print(df["sentiment_label"].value_counts())

    print("\nCreated:")
    print("output/pros_cons_sentiment.csv")


if __name__ == "__main__":
    main()