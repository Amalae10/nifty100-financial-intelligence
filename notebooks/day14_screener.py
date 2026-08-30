import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT company_id, year,
       return_on_equity_pct,
       debt_to_equity
FROM financial_ratios
WHERE year = 'Mar 2024'
  AND return_on_equity_pct > 15
  AND debt_to_equity < 1
ORDER BY return_on_equity_pct DESC
""", conn)

conn.close()

print(df.to_string(index=False))
print("\nScreener result count:", len(df))