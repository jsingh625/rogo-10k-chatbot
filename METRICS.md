# Financial Metrics Documentation

This document provides detailed information about the financial metrics implemented in the SEC Financial Chatbot.

## Overview

The metrics system provides the following capabilities:
- Calculate standard financial metrics from raw financial data
- Support for complex compound metrics derived from multiple inputs
- Classification of metrics by financial statement type
- Alias resolution for commonly used alternative names
- Data validation to ensure required inputs are available

## Metric Categories

The metrics are organized into the following categories:

1. **Income Statement Metrics** - Revenue, expenses, and profit
2. **Balance Sheet Metrics** - Assets, liabilities, and equity
3. **Cash Flow Metrics** - Operating, investing, and financing cash flows
4. **Ratios & Margins** - Profitability and efficiency ratios
5. **Growth Metrics** - Year-over-year changes in key metrics
6. **Per Share Metrics** - EPS and related metrics
7. **Return Metrics** - ROE, ROA, ROIC, etc.
8. **Liquidity Metrics** - Current ratio, quick ratio, etc.
9. **Valuation Metrics** - P/E, EV/EBITDA, etc.

## Metric Naming Conventions

- Basic metrics use simple names: `revenue`, `net_income`, `total_assets`, etc.
- Percentage/ratio metrics end with `_pct`: `net_margin_pct`, `roe_pct`, etc.
- Financial statement items are prefixed with their source:
  - Income statement: `is.NetRevenue`, `is.OperatingIncome`, etc.
  - Balance sheet: `bs.TotalAssets`, `bs.TotalLiabilities`, etc.
  - Cash flow: `cf.CashFromOperations`, `cf.CapEx`, etc.

## Available Metrics

The system includes over 80 financial metrics covering all major aspects of financial analysis.

### Core Income Statement Metrics

- `revenue` - Total top-line sales
- `cogs` - Cost of goods/services
- `gross_profit` - Revenue minus COGS
- `rnd` - Research & development expenses
- `sga` - Selling, general & administrative expenses
- `operating_income` - EBIT; income from operations
- `ebit` - Synonym for operating income
- `interest_expense` - Net interest cost
- `ebt` - Earnings before tax
- `tax_expense` - Provision for income taxes
- `net_income` - Bottom-line profit
- `eps_basic` - Earnings per share, basic
- `eps_diluted` - Earnings per share, diluted

### Balance Sheet Metrics

- `cash` - Cash & cash equivalents
- `short_term_investments` - Marketable securities
- `accounts_receivable` - Money owed by customers
- `inventory` - Goods ready for sale
- `current_assets` - Assets expected to be consumed within 1 year
- `ppe` - Property, plant & equipment
- `intangible_assets` - Non-physical assets (patents, etc.)
- `goodwill` - Premium paid above fair value in acquisitions
- `total_assets` - Total company assets
- `accounts_payable` - Money owed to suppliers
- `accrued_expenses` - Expenses recognized but not yet paid
- `short_term_debt` - Debt due within 1 year
- `current_liabilities` - Liabilities due within 1 year
- `long_term_debt` - Debt due beyond 1 year
- `total_liabilities` - All liabilities
- `shareholders_equity` - Book value; assets minus liabilities

### Cash Flow Metrics

- `cfo` - Cash from operations
- `capex` - Capital expenditures
- `cfi` - Cash from investing
- `cff` - Cash from financing
- `fcf` - Free cash flow

### Key Ratios & Margins

- `gross_margin_pct` - Gross profit margin
- `operating_margin_pct` - EBIT margin
- `net_margin_pct` - Net profit margin
- `ebitda` - EBIT + depreciation & amortization
- `ebitda_margin_pct` - EBITDA margin
- `roa_pct` - Return on assets
- `roe_pct` - Return on equity
- `roce_pct` - Return on capital employed
- `rd_pct` - R&D as % of sales
- `sga_pct` - SG&A as % of sales
- `fcf_margin_pct` - FCF as % of revenue

## Metric Formulas

Examples of metric formulas:

- `gross_profit = revenue - cogs`
- `gross_margin_pct = gross_profit / revenue`
- `net_margin_pct = net_income / revenue`
- `roe_pct = net_income / shareholders_equity`
- `ebitda = operating_income + is.D&A`
- `free_cash_flow = cfo + capex` (note: capex is typically negative)
- `current_ratio = current_assets / current_liabilities`

## Using the Metrics in Code

### Calculating a Metric

```python
from backend.metrics_interpreter import MetricsInterpreter, METRICS

# Create a metrics interpreter instance
interpreter = MetricsInterpreter()

# Company financial data
financial_data = {
    "is.NetRevenue": 100.0,
    "is.CostOfRevenue": 60.0,
    "is.OperatingIncome": 15.0,
    "is.NetIncome": 10.0,
    "bs.TotalAssets": 200.0,
    "bs.TotalEquity": 100.0
}

# Calculate a simple metric
result = interpreter.calculate_metric("revenue", financial_data)
if result["success"]:
    print(f"Revenue: {result['value']} million")
    
# Calculate a compound metric
result = interpreter.calculate_metric("net_margin_pct", financial_data)
if result["success"]:
    print(f"Net Margin: {result['value']}%")
```

### Using Metric Aliases

The system supports common alternative names for metrics:

```python
# These all calculate the same metric
interpreter.calculate_metric("revenue", data)
interpreter.calculate_metric("sales", data)
interpreter.calculate_metric("top_line", data)
```

### Identifying Metrics in Natural Language

The system can identify which metrics are being requested in a natural language query:

```python
query = "What was Apple's net profit margin in 2023?"
metrics = interpreter.identify_metrics(query)
# Results in: ["net_margin_pct"]
```

## Utilities

The `metrics_utils.py` module provides additional utilities:

- List all available metrics with `list_available_metrics()`
- Find metrics matching a keyword with `find_metrics_by_keyword()`
- Get detailed information about a metric with `get_metric_requirements()`
- Export the metrics dictionary to various formats with `export_metrics_dictionary()`

## Notes on Metric Calculations

- Monetary amounts are typically in millions of USD
- Percentage values are stored as decimals (0.25 for 25%) and displayed as percentages
- Time-series metrics (e.g., growth rates) use `_t` suffix for current period and `_t-1` for previous period
- Always check if required inputs are available before calculating a metric

## Best Practices

1. Always validate that required inputs are available before calculating metrics
2. Prefer direct calculations over nested ones for better performance
3. Use `get_metric_requirements()` to understand the full dependency chain for complex metrics
4. Pay attention to units of measurement (millions/billions) and currency
5. For percentages, verify whether the calculated value is already in percentage form 