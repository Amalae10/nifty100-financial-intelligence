# Nifty100 Financial Intelligence Platform

A financial intelligence and analytics platform for Nifty 100 companies built using Python, Pandas, SQLite, Plotly, and Streamlit.

The platform ingests and validates financial data, calculates financial KPIs, performs peer and valuation analysis, provides financial screening, and presents the results through an interactive Streamlit dashboard.

This project is developed as part of the Bluestock FinTech internship project.

---

## Project Overview

The Nifty100 Financial Intelligence Platform provides financial analytics for 92 Nifty 100 companies.

The platform currently includes:

- Financial data ETL pipeline
- Data quality validation
- SQLite financial database
- Financial ratio and KPI engine
- CAGR and cash-flow analytics
- Composite financial health scoring
- Financial screener
- Peer comparison engine
- Peer percentile analysis
- Capital allocation classification
- Valuation analysis
- Interactive Streamlit dashboard
- Annual report access

---

## Tech Stack

- Python
- Pandas
- NumPy
- SQLite
- SQL
- Streamlit
- Plotly
- OpenPyXL
- Pytest
- Git
- GitHub

---

## Sprint 1 — Data Foundation

Sprint 1 established the core financial data foundation.

### Key Deliverables

- ETL pipeline for financial datasets
- Financial year and ticker normalization
- 16 data quality rules (`DQ-01` to `DQ-16`)
- Relational SQLite database
- Primary and foreign key validation
- Load audit report
- Validation failure report
- Exploratory SQL analysis
- ETL unit tests

### Sprint 1 Results

```text
Companies: 92
Foreign Key Violations: 0
CRITICAL DQ Failures: 0
ETL Tests: 54 passed
```

The main database is:

```text
nifty100.db
```

Validation output:

```text
output/validation_failures.csv
```

Load audit:

```text
output/load_audit.csv
```

---

## Sprint 2 — Financial Ratio Engine

Sprint 2 implemented the financial analytics and KPI calculation layer.

### Key Features

- Profitability ratios
- Leverage ratios
- Growth metrics
- Cash-flow KPIs
- Revenue CAGR
- PAT CAGR
- FCF CAGR
- Capital allocation analysis
- Composite financial score
- Ratio edge-case handling

The financial ratio engine contains historical financial metrics for the companies available in the database.

### Sprint 2 Testing

```text
KPI Tests: 37 passed
```

Important modules:

```text
src/analytics/ratios.py
src/analytics/cagr.py
src/analytics/cashflow_kpis.py
src/analytics/composite_score.py
src/analytics/populate_ratios.py
```

---

## Sprint 3 — Screener & Peer Comparison Engine

Sprint 3 added company screening, financial health scoring, and peer comparison capabilities.

### Financial Screener

The screener supports financial filtering using metrics such as:

- ROE
- Debt-to-Equity
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- Operating Profit Margin
- P/E
- P/B
- Dividend Yield
- Interest Coverage Ratio

Preset screens include:

- Quality
- Value
- Growth
- Dividend
- Debt-Free
- Turnaround

### Peer Comparison

Companies are grouped into 11 peer groups.

The peer engine provides:

- Peer percentile calculations
- 10 peer-comparison metrics
- Benchmark-company identification
- 8-axis radar charts
- Peer KPI comparison tables
- Peer comparison Excel reports

Generated outputs include:

```text
output/peer_comparison.xlsx
reports/radar_charts/
```

---

## Sprint 4 — Interactive Dashboard & Valuation

Sprint 4 introduced the interactive Streamlit dashboard and valuation module.

### Streamlit Dashboard

The dashboard contains 8 screens:

1. Home
2. Company Profile
3. Financial Screener
4. Peer Comparison
5. Trend Analysis
6. Sector Analysis
7. Capital Allocation Map
8. Annual Reports

Run the dashboard using:

```bash
streamlit run src/dashboard/app.py
```

---

## Dashboard Features

### Home

Provides an overview of the Nifty 100 financial universe, including:

- Financial KPI cards
- Sector distribution
- Composite-score leaders
- Year-based analysis

### Company Profile

Provides company-level financial analysis including:

- Company information
- Latest financial KPI cards
- Revenue and Net Profit trend
- ROE and ROCE trend
- Pros and Cons
- Partial-history handling
- Missing-data handling

### Financial Screener

Provides interactive filtering using 10 financial metrics.

Features include:

- 10 slider filters
- 6 preset strategies
- Live result count
- Sortable company table
- CSV download
- Empty-result handling

### Peer Comparison

Provides comparison against similar companies using:

- Peer-group selector
- Company selector
- 8-metric radar chart
- Peer average comparison
- KPI comparison table
- Benchmark highlighting

### Trend Analysis

Provides historical financial trend analysis.

Features include:

- Company search
- Maximum 3 metrics per chart
- 10-year historical trend
- YoY annotations
- Normalized trend comparison
- Missing-metric handling

### Sector Analysis

Provides sector-level analysis using:

- Sector selector
- Revenue vs ROE bubble chart
- Market-cap bubble sizing
- Sub-sector grouping
- Sector median KPI analysis

### Capital Allocation Map

Classifies companies according to operating, investing, and financing cash-flow patterns.

Eight capital-allocation patterns are supported:

- Shareholder Returns
- Reinvestor
- Mixed
- Liquidating Assets
- Growth Funded by Debt
- Distress Signal
- Pre-Revenue
- Cash Accumulator

The page includes:

- Interactive treemap
- Year selector
- Pattern drill-down
- Company list
- CSV download
- Partial-year data handling

### Annual Reports

Provides centralized access to historical annual reports.

Features include:

- Company search
- Available report years
- BSE PDF links
- Report availability validation
- Friendly unavailable-report indicator

---

## Valuation Module

The valuation module is implemented in:

```text
src/analytics/valuation.py
```

It calculates:

```text
FCF Yield % = Free Cash Flow / Market Capitalization × 100
```

It also calculates:

- Latest-year sector median P/E
- 5-year median P/E
- P/E vs sector median percentage
- P/B
- EV/EBITDA

### Valuation Classification

```text
P/E > Sector Median × 1.5  → Caution
P/E < Sector Median × 0.7  → Discount
Otherwise                  → Fair
```

Latest valuation results:

```text
Total Companies: 92
Fair: 48
Discount: 30
Caution: 14
```

Generated reports:

```text
output/valuation_summary.xlsx
output/valuation_flags.csv
```

`valuation_flags.csv` contains only companies classified as Caution or Discount.

---

## Data Sources

The platform processes financial datasets covering:

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Sectors
- Peer Groups
- Financial Ratios
- Market Capitalization
- Stock Prices
- Analysis
- Documents
- Pros & Cons

Raw source data is treated as read-only.

---

## Data Quality Validation

The ETL pipeline implements 16 data quality rules (`DQ-01` to `DQ-16`).

Checks include:

- Primary key uniqueness
- Company/year uniqueness
- Foreign key integrity
- Balance sheet validation
- Operating profit margin cross-check
- Positive sales validation
- Net cash flow consistency
- Tax rate validation
- Dividend payout validation
- URL validation
- EPS consistency
- Historical year coverage

CRITICAL validation failures must be resolved before data is accepted.

---

## Testing & Integration QA

Automated testing is performed using Pytest.

Run:

```bash
pytest -q
```

Sprint 4 integration QA included:

- All 8 Streamlit screens tested
- 10 companies tested across multiple sectors
- Partial historical data tested
- Missing `None` / `NaN` values tested
- Extreme screener filters tested
- Empty screener result handling tested
- Chart sizing and responsiveness checked
- Capital Allocation interaction tested
- Annual Report availability handling tested

### Company Profile Performance

Five Company Profile screens were measured against the requirement of less than 3 seconds:

| Ticker | Load Time |
|---|---:|
| TCS | 0.59 sec |
| INFY | 0.12 sec |
| HDFCBANK | 0.13 sec |
| RELIANCE | 0.12 sec |
| SUNPHARMA | 0.12 sec |

All five tests passed the `< 3 seconds` requirement.

---

## Missing & Partial Data Handling

The dashboard is designed to handle incomplete financial data safely.

Examples:

- Missing metrics display `N/A`
- Missing trend metrics display an information message
- Partial historical data displays only the available years
- A limited-data message is shown when fewer than 10 years are available
- Missing Pros & Cons display a friendly message
- Unavailable annual reports display `Report unavailable`

Missing financial values are not automatically replaced with zero because doing so could misrepresent the underlying financial data.

---

## Project Structure

```text
n100-financial-intelligence/
│
├── data/
│   ├── raw/
│   └── supporting/
│
├── src/
│   ├── etl/
│   ├── analytics/
│   └── dashboard/
│       ├── app.py
│       ├── pages/
│       └── utils/
│
├── tests/
│   ├── etl/
│   └── kpi/
│
├── notebooks/
├── output/
├── reports/
├── docs/
├── config/
│
├── nifty100.db
├── requirements.txt
├── pytest.ini
├── Makefile
└── README.md
```

---

## Running the Project

### Create the Database

```bash
python -m src.etl.create_db
```

### Load Data

```bash
python -m src.etl.load_database
```

### Run Validation

```bash
python -m src.etl.run_validation
```

### Populate Financial Ratios

```bash
python -m src.analytics.populate_ratios
```

### Generate Valuation Reports

```bash
python -m src.analytics.valuation
```

### Run Tests

```bash
pytest -q
```

### Start the Dashboard

```bash
streamlit run src/dashboard/app.py 
```

The dashboard will normally be available locally through Streamlit after the server starts.

---

## Current Project Status

```text
Sprint 1 — Data Foundation                    Completed
Sprint 2 — Financial Ratio Engine             Completed
Sprint 3 — Screener & Peer Comparison Engine  Completed
Sprint 4 — Dashboard & Valuation              Completed
```

The platform now provides a complete workflow from financial-data ingestion and validation through financial analytics, peer comparison, valuation, screening, and interactive dashboard visualization.