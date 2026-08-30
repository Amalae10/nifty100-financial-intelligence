
# checks the final KPI values for ABB, INFY, and TCS

import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT company_id, year,
       return_on_equity_pct,
       revenue_cagr_5yr
FROM financial_ratios
WHERE company_id IN ('ABB', 'TCS', 'INFY')
""", conn)

print(df.groupby("company_id").tail(3).to_string(index=False))

conn.close()