# Sprint 4 Retrospective

## Sprint Overview

Sprint 4 focused on building the Streamlit dashboard and valuation module for the N100 Financial Intelligence Platform.

The main objective was to convert the financial analytics developed in earlier sprints into an interactive application that allows users to explore companies, financial ratios, peers, sectors, trends, and reports.

## What Was Completed

- Built the Streamlit dashboard.
- Created 8 dashboard screens:
  - Home
  - Company Profile
  - Screener
  - Peer Comparison
  - Financial Trends
  - Sector Analysis
  - Capital Analysis
  - Reports
- Added shared SQLite database access functions.
- Added Streamlit caching for database queries.
- Integrated financial ratios and company information.
- Integrated peer and sector analytics.
- Implemented company selection across the dashboard.
- Added financial trend visualizations.
- Added screener filtering.
- Added CSV export from the screener.
- Built the valuation module.
- Generated valuation results for all 92 companies.
- Generated valuation classifications including Fair, Discount, and Caution.

## What Went Well

The dashboard successfully brought multiple analytics modules into one user interface.

Reusable database functions reduced repeated code across dashboard pages.

Caching improved the efficiency of repeated database queries.

The screener and company profile made the financial data easier to explore without directly querying SQLite.

## Challenges

The main challenge was ensuring that every dashboard page worked correctly for different company tickers.

Some companies had incomplete historical data, so dashboard components needed to handle missing values safely.

Integrating outputs from earlier sprints also required consistent column names and database structures.

## Key Learnings

- Streamlit can quickly convert Python analytics into an interactive application.
- Shared database utilities make multi-page applications easier to maintain.
- Caching is useful for improving dashboard performance.
- Missing financial data must be handled gracefully in user-facing applications.
- Analytics outputs should be designed for both programmatic use and visualization.

## Sprint Result

Sprint 4 was completed successfully.

The project finished the sprint with:

- 8 Streamlit dashboard screens
- 92 companies available for analysis
- Working company profile and financial trend views
- Peer and sector analytics integration
- Working financial screener
- Working CSV export
- Valuation analysis for 92 companies
- 48 Fair classifications
- 30 Discount classifications
- 14 Caution classifications

The dashboard and valuation layer were ready for the reporting and financial intelligence work in the following sprint.