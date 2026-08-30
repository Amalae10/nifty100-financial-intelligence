import sqlite3
import pandas as pd

conn=sqlite3.connect("nifty100.db")

df=pd.read_sql("SELECT * FROM financial_ratios",conn)

print("Rows:",len(df))
print("columns:",len(df.columns))

print("\nNull-only columns:")
null_only=[c for c in df.columns if df[c].isna().all()]

if null_only:
    print(null_only)

else:
    print("None")

conn.close()