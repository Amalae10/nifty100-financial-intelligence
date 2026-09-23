# Sprint 3 Retrospective

## Sprint Overview

Sprint 3 focused on building the peer comparison and sector analytics layer of the N100 Financial Intelligence Platform.

The sprint extended the financial KPI engine by allowing companies to be compared with relevant peer groups using percentile-based analysis and visual benchmarking.

## What Was Completed

- Built the peer comparison engine.
- Implemented peer analysis using 10 financial metrics.
- Generated peer percentile calculations.
- Created 560 peer percentile records.
- Covered 11 peer groups used by the project.
- Generated peer comparison outputs for all 92 companies.
- Created 92 radar charts for company-level peer analysis.
- Generated the peer analysis workbook.
- Added validation and automated tests for peer analytics.
- Completed 19 validator tests successfully.

## What Went Well

The peer analytics pipeline successfully converted company-level financial ratios into comparable peer metrics.

Percentile calculations made it easier to identify how a company performs relative to similar companies instead of relying only on absolute KPI values.

Automated testing helped verify the peer calculations and reduced the risk of incorrect comparison results.

## Challenges

The main challenge was handling differences between companies and peer groups while keeping the comparison metrics consistent.

Some companies had missing or incomplete financial information, which required careful handling during peer calculations.

Another challenge was ensuring that radar charts and percentile outputs were generated consistently for all 92 companies.

## Key Learnings

- Peer comparison provides more context than standalone financial ratios.
- Percentile rankings are useful for relative company analysis.
- Data validation is important before generating comparison metrics.
- Automated visual reports can make financial analysis easier to interpret.
- Testing analytical calculations is essential before using them in dashboards and reports.

## Sprint Result

Sprint 3 was completed successfully.

The project finished the sprint with:

- 92 companies included in peer analysis
- 10 peer comparison metrics
- 560 peer percentile records
- 11 peer groups
- 92 radar charts
- Peer analysis workbook generated
- 19 validator tests passing

The peer analytics layer was ready to be integrated into the Streamlit dashboard in Sprint 4.
