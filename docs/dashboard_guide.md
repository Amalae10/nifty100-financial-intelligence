# Nifty100 Financial Intelligence Platform — Dashboard Guide

## 1. Introduction

The Nifty100 Financial Intelligence Dashboard is an interactive Streamlit application for exploring financial information about Nifty 100 companies.

The dashboard provides company analysis, financial screening, peer comparison, trend analysis, sector analysis, capital allocation analysis, and access to annual reports.

## 2. Start the Dashboard

From the project root, run:

```bash
streamlit run src/dashboard/app.py
```

The Streamlit application will open in the browser.

---

## 3. Dashboard Navigation

The dashboard contains 8 main screens:

1. Home
2. Company Profile
3. Financial Screener
4. Peer Comparison
5. Trend Analysis
6. Sector Analysis
7. Capital Allocation Map
8. Annual Reports

Use the Streamlit sidebar to move between pages.

---

## 4. Home

The Home page provides a high-level overview of the Nifty 100 financial universe.

### Features

- Financial KPI cards
- Sector distribution
- Sector visualization
- Top companies by composite score
- Year-based financial overview

### How to Use

Select the required year and review the overall financial and sector-level information.

---

## 5. Company Profile

The Company Profile page provides detailed financial information for an individual company.

### Features

- Company search
- Company information card
- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Revenue CAGR
- Free Cash Flow
- Revenue and Net Profit history
- ROE and ROCE trend
- Pros and Cons

### How to Use

Search for a company using its ticker or company name.

The dashboard displays the latest available financial KPIs and historical trends.

If fewer than 10 years of historical data are available, the dashboard displays the available years and provides a limited-data message.

Missing financial values are displayed as `N/A`.

---

## 6. Financial Screener

The Financial Screener helps identify companies that meet selected financial conditions.

### Available Filters

- Minimum ROE
- Maximum Debt-to-Equity
- Minimum Free Cash Flow
- Minimum Revenue CAGR
- Minimum PAT CAGR
- Minimum Operating Profit Margin
- Maximum P/E
- Maximum P/B
- Minimum Dividend Yield
- Minimum Interest Coverage Ratio

### Presets

Six predefined screening strategies are available:

- Quality
- Value
- Growth
- Dividend
- Debt-Free
- Turnaround

### How to Use

Adjust the sliders manually or select a preset.

The result table updates according to the selected conditions.

The filtered results can be downloaded as CSV.

If no company satisfies the selected conditions, the dashboard displays an empty-result message instead of crashing.

---

## 7. Peer Comparison

The Peer Comparison page compares companies operating in similar business groups.

### Features

- Peer-group selector
- Company selector
- 8-metric radar chart
- Peer average comparison
- KPI comparison table
- Benchmark-company highlighting

### How to Use

First select a peer group.

Then select a company from that group.

The radar chart compares the selected company's percentile performance with the peer-group average.

The table below displays financial KPIs for companies in the selected peer group.

The benchmark company is highlighted for easy identification.

### Benchmark Meaning

The benchmark is the designated reference company for the peer group.

It does not mean that the benchmark company is automatically the best company for every financial KPI.

---

## 8. Trend Analysis

The Trend Analysis page is used to study changes in financial metrics over time.

### Features

- Company search
- Multi-metric selection
- Maximum of 3 metrics
- Historical trend chart
- YoY annotations
- Normalized comparison

### How to Use

Select a company and choose up to three financial metrics.

The chart displays the historical movement of the selected metrics.

When metrics use very different units, normalized values allow their trends to be compared on a common scale.

If a selected metric is unavailable for a company, it is skipped and an information message is displayed.

---

## 9. Sector Analysis

The Sector Analysis page compares companies within a selected sector.

### Features

- Sector selector
- Revenue vs ROE bubble chart
- Market Capitalization represented by bubble size
- Sub-sector grouping
- Sector median KPI analysis

### How to Use

Select a sector from the dropdown.

The bubble chart displays:

```text
X-axis     → Revenue
Y-axis     → ROE
Bubble size → Market Capitalization
Color/group → Sub-sector
```

The median KPI section allows the user to inspect sector-level median financial metrics.

Individual median metrics are displayed separately because Revenue, ROE, and Market Capitalization use different units and scales.

---

## 10. Capital Allocation Map

The Capital Allocation page analyzes how companies generate and use cash.

The classification uses the signs of:

- Cash Flow from Operating Activities (CFO)
- Cash Flow from Investing Activities (CFI)
- Cash Flow from Financing Activities (CFF)

### Capital Allocation Patterns

The platform supports 8 patterns:

1. Shareholder Returns
2. Reinvestor
3. Mixed
4. Liquidating Assets
5. Growth Funded by Debt
6. Distress Signal
7. Pre-Revenue
8. Cash Accumulator

### Features

- Year selector
- Interactive treemap
- Capital-allocation classification
- Pattern drill-down
- Company list
- CSV download

### How to Use

Select a financial year.

The treemap groups companies according to their capital-allocation pattern.

Select a pattern to display the companies belonging to that category.

Some historical years may contain fewer companies because financial data is not available for every company in every year.

---

## 11. Annual Reports

The Annual Reports page provides access to historical company annual reports.

### Features

- Company search
- Historical report years
- BSE annual-report links
- Link availability checking

### How to Use

Select a company.

The page displays the available report years.

When the report is accessible, use the `Open BSE PDF` button.

When a report cannot be accessed, the dashboard displays:

```text
Report unavailable
```

---

## 12. Missing Data Handling

The dashboard handles incomplete financial information without crashing.

Examples include:

- Missing KPI → `N/A`
- Missing historical metric → information message
- Partial history → available years are displayed
- Missing Pros and Cons → friendly information message
- Missing annual report → `Report unavailable`

Missing financial data is not automatically replaced with zero because zero could incorrectly represent the company's actual financial position.

---

## 13. Downloads

Depending on the page, users can export results such as:

- Screener results → CSV
- Capital Allocation company list → CSV
- Peer comparison analysis → Excel

Generated analytical reports are stored inside the project's `output/` and `reports/` directories.

---

## 14. Performance

Company Profile performance was tested using five different companies.

All tested profiles loaded within the required limit of:

```text
< 3 seconds
```

The dashboard was also tested with companies containing complete and partial historical data.

---

## 15. Integration QA

Before Sprint 4 completion, the dashboard was tested for:

- All 8 Streamlit screens
- 10 companies across multiple sectors
- Partial historical data
- Missing financial metrics
- Extreme screener conditions
- Empty screener results
- Chart responsiveness
- Capital Allocation interactions
- Annual-report availability
- Company Profile performance

All critical dashboard functionality passed integration QA.

---

## 16. Troubleshooting

If Streamlit produces a Windows connection-reset or file-watcher issue, run:

```bash
streamlit run src/dashboard/app.py --server.fileWatcherType none
```

Make sure the virtual environment is activated and all packages from `requirements.txt` are installed.

---

## Dashboard Status

```text
Home                    PASS
Company Profile         PASS
Financial Screener      PASS
Peer Comparison         PASS
Trend Analysis          PASS
Sector Analysis         PASS
Capital Allocation      PASS
Annual Reports          PASS

Sprint 4 Dashboard QA   COMPLETE
```