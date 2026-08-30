# Nifty100 Financial Intelligence Platform

A financial data intelligence platform built using Python, Pandas, SQL, and SQLite to ingest, validate, store, and analyze financial data for Nifty 100 companies.

This project is developed as part of the Bluestock FinTech internship project.

## Sprint 1 — Data Foundation

Sprint 1 focuses on building a reliable data foundation for future financial analytics modules.

### Objectives

- Build an ETL pipeline for financial datasets
- Normalize company tickers and financial years
- Implement data quality validation rules
- Create a relational SQLite database
- Load financial datasets into the database
- Validate primary and foreign key relationships
- Perform manual data quality review
- Run exploratory SQL analysis

## Tech Stack

- Python
- Pandas
- SQLite
- SQL
- Pytest
- Git
- GitHub

## Project Structure

```text
n100-financial-intelligence/
│
├── data/raw/                   # Raw financial datasets
├── db/
│   └── schema.sql              # SQLite database schema
│
├── src/etl/
│   ├── loader.py               # CSV loading utilities
│   ├── normaliser.py           # Year and ticker normalization
│   ├── validator.py            # DQ-01 to DQ-16
│   ├── run_validation.py       # Runs validation
│   ├── create_db.py            # Creates SQLite database
│   └── load_database.py        # Full database load
│
├── tests/etl/                  # ETL unit tests
├── notebooks/
│   └── exploratory_queries.sql # 10 exploratory SQL queries
│
├── output/
│   ├── load_audit.csv
│   └── validation_failures.csv
│
├── docs/
│   └── sprint1_retrospective.md
│
├── requirements.txt
├── Makefile
└── README.md
```

## Data Sources

The project processes financial datasets covering:

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

## Data Quality Validation

The ETL pipeline implements 16 data quality rules (`DQ-01` to `DQ-16`).

The checks include:

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

Validation issues are written to:

```text
output/validation_failures.csv
```

CRITICAL issues must be resolved before the data is accepted.

## Database

The processed data is stored in:

```text
nifty100.db
```

Foreign key enforcement is enabled using:

```sql
PRAGMA foreign_keys = ON;
```

Final Sprint 1 database checks:

```text
Companies: 92
Foreign Key Violations: 0
CRITICAL DQ Failures: 0
```

## Load Audit

Every data load is recorded in:

```text
output/load_audit.csv
```

The audit tracks:

```text
table
rows_read
rows_loaded
rows_rejected
critical_rejections
```

This makes the ETL process traceable and helps identify rows removed during cleaning.

## Testing

The ETL pipeline is tested using Pytest.

Run:

```bash
pytest -q
```

Sprint 1 result:

```text
54 passed
0 failed
```

## Exploratory SQL Analysis

Ten exploratory SQL queries are available in:

```text
notebooks/exploratory_queries.sql
```

They cover:

- Company counts
- Financial statement analysis
- Top companies by sales
- Top companies by net profit
- ROE analysis
- Sector distribution
- Historical data coverage
- Market capitalization
- Company and financial-data joins

## Sprint 1 Results

Sprint 1 successfully delivered:

- SQLite financial database
- Full ETL pipeline
- 16 data quality rules
- Zero unresolved CRITICAL validation failures
- Zero foreign key violations
- 54 passing unit tests
- Load audit report
- Validation failure report
- Manual review of 5 companies
- 10 exploratory SQL queries

## Running the Project

Create the database:

```bash
python -m src.etl.create_db
```

Load the data:

```bash
python -m src.etl.load_database
```

Run validation:

```bash
python -m src.etl.run_validation
```

Run tests:

```bash
pytest -q
```

## Current Status

**Sprint 1 — Data Foundation: Completed**

The data foundation is ready for the next phase of the Nifty100 Financial Intelligence Platform.