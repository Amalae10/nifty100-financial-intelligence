import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE company_id IN ('ABB','INFY','TCS','RELIANCE','HDFCBANK')
  AND year = 'Mar 2024'
""", conn)

conn.close()

print(df.to_string(index=False))
print("\nCompanies demonstrated:", len(df))