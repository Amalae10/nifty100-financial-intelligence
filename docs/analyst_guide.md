# Nifty100 Financial Intelligence Platform
## Analyst Guide

### Version 1.0

This guide explains how analysts can use the Nifty100 Financial Intelligence Platform for financial analysis, company screening, peer comparison, valuation, cash-flow analysis, clustering, and report generation.

The platform currently covers 92 companies and combines financial data processing, analytics, visualization, and REST API access in a single system.

---

# 1. Introduction

## 1.1 Purpose

The Nifty100 Financial Intelligence Platform is designed to help financial analysts explore and compare company financial performance using structured financial data.

The platform converts raw financial information into useful analytical outputs such as:

- Financial ratios and KPIs
- Revenue and profit growth metrics
- Cash-flow indicators
- Financial health scores
- Company screening results
- Peer comparisons
- Valuation indicators
- Capital-allocation classifications
- Company clusters
- Company reports and tear sheets

The system also provides an interactive Streamlit dashboard and a FastAPI REST API.

---

## 1.2 Company Coverage

The current database contains:

```text
92 companies
```

The companies are organized using sector and peer-group information to support comparison and benchmarking.

Some companies may have incomplete historical information. The platform handles missing information without automatically converting unavailable financial values to zero.

---

## 1.3 Main Components

The platform contains the following major components:

1. ETL and data normalization
2. Data-quality validation
3. SQLite financial database
4. Financial KPI engine
5. Financial screener
6. Peer comparison engine
7. Valuation module
8. Streamlit dashboard
9. NLP-based Pros & Cons processing
10. Cash-flow intelligence
11. Capital-allocation analysis
12. Company clustering
13. FastAPI REST API
14. Automated testing and performance validation
15. Financial reports and exports

---

# 2. System Architecture

## 2.1 High-Level Data Flow

The platform follows this general workflow:

```text
Raw Financial Data
        |
        v
ETL / Normalization
        |
        v
Data Quality Validation
        |
        v
SQLite Database
        |
        v
Financial KPI Engine
        |
        +-------------------+
        |                   |
        v                   v
Analytics Modules      FastAPI REST API
        |
        v
Streamlit Dashboard
        |
        v
Reports / CSV / Excel / PDF
```

Raw data is first loaded and normalized. Data-quality rules are then applied before the information is used for financial calculations and analytics.

---

## 2.2 Main Technology Stack

The platform uses:

```text
Python
Pandas
NumPy
SQLite
SQL
Streamlit
Plotly
FastAPI
Pytest
OpenPyXL
Git
GitHub
```

Python and Pandas perform the main data-processing operations.

SQLite provides the local financial database.

Streamlit provides the interactive analyst dashboard.

FastAPI provides programmatic REST API access to the platform.

Pytest is used for automated quality assurance.

---

# 3. Data Sources and Database

## 3.1 Financial Data

The platform processes data covering:

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Financial Ratios
- Sectors
- Peer Groups
- Market Capitalization
- Stock Prices
- Analysis
- Documents
- Pros & Cons

Raw source data is treated as read-only.

The ETL pipeline performs the required cleaning and normalization before loading data into the analytical database.

---

## 3.2 SQLite Database

The main database is:

```text
nifty100.db
```

The database provides centralized access to company financial information used throughout the project.

Important financial tables include:

```text
companies
profitandloss
balancesheet
cashflow
financial_ratios
sectors
market_cap
stock_prices
documents
analysis
```

Additional tables support peer comparison and other analytical features.

---

## 3.3 Database Optimization

Indexes are used on frequently queried company/year fields.

Indexes were added for:

```text
financial_ratios(company_id, year)
profitandloss(company_id, year)
balancesheet(company_id, year)
cashflow(company_id, year)
```

These indexes improve repeated company and financial-year queries used by the API and analytics modules.

---

# 4. ETL and Data Quality

## 4.1 ETL Process

ETL means:

```text
Extract
Transform
Load
```

The ETL layer reads the financial source files, standardizes important fields, validates the information, and loads it into SQLite.

Important ETL modules are located under:

```text
src/etl/
```

---

## 4.2 Normalization

Normalization ensures that values from different source files follow a consistent format.

Examples include:

- Financial-year normalization
- Company ticker normalization
- Column consistency
- Missing-value handling

Consistent values are important because financial information from different tables must be joined using company and year identifiers.

---

## 4.3 Data Quality Rules

The project implements 16 data-quality rules:

```text
DQ-01 to DQ-16
```

The validation process checks areas such as:

- Primary-key uniqueness
- Company/year uniqueness
- Foreign-key integrity
- Balance-sheet consistency
- Positive sales
- Operating margin consistency
- Net cash-flow consistency
- Tax values
- Dividend payout
- EPS consistency
- Historical coverage
- Document URL validation

Critical failures must be resolved before the data is considered ready for analytical use.

Validation results can be written to:

```text
output/validation_failures.csv
```

---

## 4.4 Why Data Quality Matters

Financial analytics depend on reliable source data.

For example, duplicate company/year records can distort growth calculations, while incorrect cash-flow values can affect free-cash-flow analysis.

The validation layer therefore acts as a quality checkpoint between the source data and the analytical modules.

---

# 5. Financial KPI Engine

## 5.1 Purpose

The KPI engine converts raw financial statements into metrics that analysts can use to evaluate profitability, leverage, growth, cash flow, valuation, and operating performance.

The main analytics modules are located in:

```text
src/analytics/
```

Important modules include:

```text
ratios.py
cagr.py
cashflow_kpis.py
composite_score.py
```

---

## 5.2 Profitability Metrics

Profitability metrics help analysts understand how efficiently a company generates profit.

Examples include:

- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Operating Profit Margin (OPM)
- Net Profit Margin

Higher profitability does not automatically mean that a company is better. Analysts should compare profitability with historical performance, leverage, cash flow, valuation, and relevant peers.

---

## 5.3 Growth Metrics

The platform calculates historical growth indicators including:

```text
Revenue CAGR
PAT CAGR
FCF CAGR
```

CAGR means Compound Annual Growth Rate.

These metrics help analysts understand longer-term growth instead of relying only on a single year's change.

The platform includes 5-year growth measures used by the screener and clustering modules.

---

## 5.4 Cash-Flow Metrics

Cash-flow analysis helps determine whether reported accounting profits are supported by actual cash generation.

The platform analyzes:

- Operating cash flow
- Investing cash flow
- Financing cash flow
- Free cash flow
- CFO/PAT relationship

These metrics are also used in capital-allocation and financial-health analysis.

---

# 6. Financial Screener

## 6.1 Purpose

The financial screener allows analysts to filter companies according to financial conditions.

The Streamlit dashboard provides an interactive screener, while the FastAPI service also exposes screening functionality.

---

## 6.2 Available Screening Metrics

The platform supports filters including:

- ROE
- Debt-to-Equity
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- Operating Profit Margin
- P/E
- P/B
- Dividend Yield
- Interest Coverage

The API screener supports parameters such as:

```text
min_roe
max_de
min_fcf
sector
min_rev_cagr_5yr
min_pat_cagr_5yr
max_pe
```

---

## 6.3 Example Screening Workflow

An analyst looking for companies with ROE of at least 15% can use:

```text
GET /api/v1/screener?min_roe=15
```

The dashboard can perform similar filtering using interactive controls.

Analysts should treat screening as a method for narrowing the company universe rather than as an automatic investment recommendation.

---

## 6.4 Screener Export

The Streamlit screener supports CSV export.

This allows filtered results to be downloaded for additional analysis using tools such as Excel, Python, or other analytical software.

---

# 7. Peer Comparison

## 7.1 Purpose

Peer comparison evaluates a company relative to businesses with similar characteristics.

The platform contains:

```text
11 peer groups
```

Peer analysis is useful because financial ratios can vary substantially across industries and business models.

---

## 7.2 Peer Metrics

The peer engine uses 10 comparison metrics.

These include profitability, leverage, growth, cash-flow, and operating-performance measures.

Peer percentile calculations allow analysts to understand where a company stands relative to its peer group.

---

## 7.3 Radar Comparison

The dashboard provides an 8-metric radar visualization.

The radar view can compare:

```text
Selected Company
Peer Group Average
Benchmark Company
```

This provides a visual summary of relative financial strengths and weaknesses.

---

## 7.4 Peer Outputs

Generated peer-analysis outputs include:

```text
output/peer_comparison.xlsx
reports/radar_charts/
```

The API also exposes peer-group and company-comparison endpoints.

---

# 8. Valuation Analysis

## 8.1 Purpose

The valuation module helps analysts compare company valuation metrics against historical and sector benchmarks.

The module is located at:

```text
src/analytics/valuation.py
```

---

## 8.2 FCF Yield

Free Cash Flow Yield compares free cash flow with market capitalization.

Conceptually:

```text
FCF Yield % = Free Cash Flow / Market Capitalization × 100
```

A valuation metric should not be interpreted independently. Analysts should consider company quality, growth, leverage, sector characteristics, and historical performance.

---

## 8.3 P/E Analysis

The platform compares company P/E against:

- Latest sector median P/E
- Historical 5-year median P/E

The current classification logic uses three labels:

```text
P/E > Sector Median × 1.5  → Caution
P/E < Sector Median × 0.7  → Discount
Otherwise                  → Fair
```

These labels describe the platform's rule-based valuation classification and should not be interpreted as buy or sell recommendations.

---

## 8.4 Current Valuation Output

The current valuation analysis covers 92 companies:

```text
Fair: 48
Discount: 30
Caution: 14
Total: 92
```

Generated files include:

```text
output/valuation_summary.xlsx
output/valuation_flags.csv
```

`valuation_flags.csv` contains companies classified as Discount or Caution under the platform's valuation rules.

---

# 9. Using the Streamlit Dashboard

## 9.1 Starting the Dashboard

Run:

```bash
streamlit run src/dashboard/app.py
```

The dashboard provides 8 analytical screens.

---

## 9.2 Dashboard Screens

The available screens are:

1. Home
2. Company Profile
3. Financial Screener
4. Peer Comparison
5. Trend Analysis
6. Sector Analysis
7. Capital Allocation Map
8. Annual Reports

---

## 9.3 Company Profile

The Company Profile screen provides company-level information including:

- Financial KPI cards
- Revenue trends
- Net-profit trends
- ROE and ROCE trends
- Pros & Cons
- Historical financial information

Missing information is displayed safely rather than automatically being converted to zero.

---

## 9.4 Trend Analysis

The Trend Analysis screen allows historical company metrics to be compared over time.

It supports:

- Company selection
- Multiple financial metrics
- Historical trends
- YoY information
- Normalized comparison
- Missing-data handling

This view is useful for identifying whether financial performance is improving, deteriorating, or remaining relatively stable over time.

---

## 9.5 Sector Analysis

The Sector Analysis screen provides sector-level comparison.

Features include:

- Sector selection
- Revenue vs ROE visualization
- Market-cap-based bubble sizing
- Sub-sector grouping
- Sector median KPI analysis

Sector analysis provides context when interpreting company-level financial metrics.

---

## 9.6 Annual Reports

The Annual Reports screen provides access to available historical company documents.

The platform contains document metadata and links, while unavailable reports are handled with a user-friendly status instead of causing the dashboard to fail.

For more detailed dashboard instructions, refer to:

```text
docs/dashboard_guide.md
```

---
