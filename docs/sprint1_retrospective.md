# Sprint 1 Retrospective

## What Went Well
- Loaded all financial datasets into SQLite.
- Implemented DQ-01 to DQ-16.
- Resolved all CRITICAL data-quality failures.
- Created PK/FK relationships.
- 54 ETL unit tests passed.
- Foreign key check returned 0 violations.
- Completed manual review of 5 companies.

## Challenges
- Duplicate company/year records.
- Invalid company IDs.
- Different year formats and TTM values.
- CSV and database schema mismatches.
- Some financial values generated DQ warnings.

## Improvements
- Normalize data before database loading.
- Keep database schema synchronized with source files.
- Track rejected rows in load_audit.csv.
- Review WARNING records without changing valid source data.

## Final Result
Sprint 1 Data Foundation completed successfully.
