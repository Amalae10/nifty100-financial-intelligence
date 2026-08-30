# Sprint 2 Retrospective — Financial Ratio Engine

## Completed Work

Sprint 2 implemented the Financial Ratio Engine for the Nifty100 Financial Intelligence Platform.

The engine calculates profitability, leverage, efficiency, CAGR and cash-flow KPIs for company-year records.

## Formula Decisions

### Profitability
- Net Profit Margin = Net Profit / Sales × 100
- Operating Profit Margin = Operating Profit / Sales × 100
- ROE = Net Profit / (Equity Capital + Reserves) × 100
- ROCE = EBIT / (Equity Capital + Reserves + Borrowings) × 100
- ROA = Net Profit / Total Assets × 100

### Leverage and Efficiency
- Debt-to-Equity = Borrowings / (Equity Capital + Reserves)
- Interest Coverage = (Operating Profit + Other Income) / Interest
- Net Debt = Borrowings - Investments
- Asset Turnover = Sales / Total Assets

Financial-sector companies are excluded from the standard high D/E warning.

## CAGR Decisions

CAGR supports:
- Normal positive growth
- DECLINE_TO_LOSS
- TURNAROUND
- BOTH_NEGATIVE
- ZERO_BASE
- INSUFFICIENT

TTM rows are excluded from historical CAGR calculations.

## Cash Flow Decisions

- Free Cash Flow = CFO + CFI
- CFO Quality uses CFO / PAT
- CapEx Intensity uses absolute investing cash flow / Sales
- FCF Conversion = FCF / Operating Profit

Capital allocation uses CFO, CFI and CFF sign patterns.

## Edge Cases

ROE and ROCE were compared against source company values.

42 anomalies were identified:
- 20 version differences
- 13 data source issues
- 9 formula discrepancies

Computed engine values are retained for analytics while source values are retained for reference.

The dataset contains 23 Financial-sector companies while the Sprint specification expected 19. This was documented as a dataset/version difference.

## Validation

- financial_ratios rows: 1,164
- KPI unit tests: 37 passed, 0 failed
- Screener ROE > 15% and D/E < 1: 37 companies
- Manual checks completed for ABB, INFY and TCS
- Manual ROE and Revenue CAGR matched engine values within 0.1%