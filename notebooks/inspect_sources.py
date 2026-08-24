from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")


def inspect_files():
    files = list(DATA_DIR.glob("*.csv"))

    print(f"Found {len(files)} CSV files\n")

    for file in files:
        print("=" * 70)
        print(f"FILE: {file.name}")

        try:
            df = pd.read_csv(file)

            print(f"Rows: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            print(f"Column names: {list(df.columns)}")

        except Exception as e:
            print(f"ERROR: {e}")

        print()


if __name__ == "__main__":
    inspect_files()