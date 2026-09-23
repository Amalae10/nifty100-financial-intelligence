# Nifty100 Financial Intelligence API Guide

## Overview

The Nifty100 Financial Intelligence API provides REST access to company financial data, financial ratios, screening, sector analytics, peer comparison, valuation, portfolio statistics, documents, and system health.

## Start the API

```bash
uvicorn src.api.main:app --reload
```

Default local server:

```text
http://127.0.0.1:8000
```

## Swagger Documentation

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Base Path

```text
/api/v1
```

## Main API Areas

The API contains 16 endpoints covering:

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Financial Ratios
- Financial Screener
- Sectors
- Peer Groups
- Peer Comparison
- Market Capitalization / Valuation
- Portfolio Statistics
- Documents
- Health Monitoring

## Example Requests

### Health Check

```text
GET /api/v1/health
```

Returns API status and database table counts.

### List Companies

```text
GET /api/v1/companies
```

Returns the available company universe.

### Company Details

```text
GET /api/v1/companies/TCS
```

### Financial Screener

```text
GET /api/v1/screener?min_roe=15
```

Returns companies satisfying the supplied financial filters.

### Sector Companies

```text
GET /api/v1/sectors/Information%20Technology
```

### Peer Comparison

```text
GET /api/v1/peers/compare/INFY
```

## API Testing

API tests are located in:

```text
tests/api/
```

The complete automated test suite can be run using:

```bash
pytest tests/
```

Generate the HTML test report using:

```bash
pytest tests/ --html=reports/pytest_report.html
```

Latest verified result:

```text
114 passed
0 failed
```

## Performance

A 50-request concurrent load test produced:

```text
Successful requests: 50/50
Average latency: 0.1210 seconds
Maximum latency: 0.1616 seconds
```

## API Documentation Files

OpenAPI specification:

```text
docs/openapi.json
```

Postman collection:

```text
docs/postman_collection.json
```