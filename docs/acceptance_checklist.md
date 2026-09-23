# N100 Financial Intelligence Platform
## Final Acceptance Checklist — Day 45

### Acceptance Criteria

| ID | Acceptance Criterion | Evidence / Result | Status |
|---|---|---|---|
| AC-01 | Data Coverage | 92 companies loaded | PASS |
| AC-02 | Time Coverage | 85/92 companies (92.39%) have >=10 years across P&L, Balance Sheet and Cash Flow | PASS |
| AC-03 | Schema Integrity | SQLite foreign-key validation returned 0 violations | PASS |
| AC-04 | KPI Completeness | financial_ratios contains 1,164 rows. KPI calculations are populated where required source inputs exist. Remaining NULLs were traced to missing source records, missing source values, or undefined formula cases such as zero denominators. | PASS WITH SOURCE-DATA EXCEPTIONS |
| AC-05 | CAGR Accuracy | Manual 5Y Revenue CAGR checks: TCS 10.4636%, INFY 13.1991%, RELIANCE 9.6061%. All exactly match stored Ratio Engine values; difference 0.0000%. | PASS |
| AC-06 | ROE Accuracy | Five-company latest-year spot check within ±5 percentage points: MARUTI, DLF, TORNTPHARM, BHEL, JSWSTEEL. TCS source ROE anomaly is documented separately in the technical specification. | PASS |
| AC-07 | Screener Accuracy | Quality preset (ROE >15, D/E <1, FCF >0) returned 20 companies | PASS |
| AC-08 | Dashboard Load | Company profile tested at approximately 0.59 seconds, below 3-second requirement | PASS |
| AC-09 | Dashboard Export | Screener CSV export generated successfully with valid headers | PASS |
| AC-10 | PDF Quality | Five sample tearsheets visually checked for overflow/overlap | PASS |
| AC-11 | API Health | /api/v1/health returned HTTP 200, status=ok, version=1.0.0 and counts for all 10 required tables | PASS |
| AC-12 | API Accuracy | TCS ratios endpoint returned >=10 non-TTM years | PASS |
| AC-13 | API Screener | API screener output verified against screener/database logic | PASS |
| AC-14 | Peer Coverage | All 11 peer groups contain member tickers | PASS |
| AC-15 | Cluster Coverage | All 92 companies assigned to clusters 0-4 with no null cluster assignments | PASS |
| AC-16 | NLP Coverage | All 92 companies have at least one generated Pro and one generated Con | PASS |
| AC-17 | Report Coverage | 92/92 company tearsheets generated. Smallest PDF approximately 71.1 KB, above 50 KB requirement | PASS |
| AC-18 | Automated Tests | Final run: 114 passed in 3.96s, 0 failures, 0 errors | PASS |
| AC-19 | Validation Report | validation_failures.csv contains required company_id, field, issue and severity columns | PASS |
| AC-20 | Analyst Guide | analyst_guide.pdf = 26 pages and contains dedicated Financial Screener and Streamlit Dashboard sections | PASS |

## Important QA Notes

### AC-04 — Source-data exceptions

The raw financial source datasets were not modified to artificially remove NULL values.

Large KPI NULL groups were traced to missing Balance Sheet or Cash Flow company-year records. Remaining exceptions in complete-source rows were traced to source-level missing values or mathematically undefined calculations.

Examples include:

- Interest Coverage: NULL when interest is zero.
- ADANIENSOL Mar 2014: zero sales/assets and other zero source values.
- PNB: operating_profit missing in source records.
- HDFCLIFE Mar 2013-2014: operating/investing cash-flow values missing.
- JIOFIN, LICI and SIEMENS: specific EPS source values missing.
- Some dividend payout source values are missing.

These values were left NULL rather than replacing them with fabricated zero values.

### AC-05 — CAGR Validation

The Ratio Engine defines 5-year CAGR using the observation exactly five years before the current year.

For Mar 2024:

- TCS: Mar 2019 -> Mar 2024 = 10.4636%
- INFY: Mar 2019 -> Mar 2024 = 13.1991%
- RELIANCE: Mar 2019 -> Mar 2024 = 9.6061%

All three manual calculations matched the stored Ratio Engine values exactly.

### AC-06 — ROE Validation

Five latest-year companies were manually compared against companies.roe_percentage and were within the required ±5 percentage-point tolerance.

The technical specification separately identifies the TCS pre-computed ROE value as anomalous and instructs analytics to use the Ratio Engine value. Raw source data was not modified.

### Test Environment

The final test suite was executed using the project virtual environment:

    .\.venv\Scripts\python.exe -m pytest tests/ -q

Result:

    114 passed in 3.96s

A previous collection error occurred when pytest was accidentally executed using the global Python environment where FastAPI was not installed. No application-code change was required.

## Final Validation Result

All 20 acceptance criteria have been checked.

Result: 20/20 acceptance criteria recorded as PASS, with AC-04 carrying documented source-data exceptions.

The project is ready for final review and Team Lead sign-off.