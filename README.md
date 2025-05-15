# SEC Financial Metrics Chatbot

A financial metrics and SEC filings analysis tool that enables users to explore financial data, calculate key metrics, and answer questions about public companies.

## Features

- Query financial data for top public companies (AAPL, MSFT, AMZN, NVDA, META, etc.)
- Calculate and visualize over 80 standard financial metrics
- Compare metrics across multiple companies
- Analyze trends and year-over-year changes
- Ask natural language questions about company financials
- Export metrics to CSV, JSON, or markdown formats

## Project Structure

- `backend/metrics_interpreter.py` - Core metrics definitions and calculation logic
- `metrics_utils.py` - Utility functions for working with the metrics
- `metrics_dashboard_demo.py` - Interactive dashboard for exploring financial metrics
- `test_metrics.py` - Test suite for the metrics system
- `METRICS.md` - Comprehensive documentation of available metrics
- `README.md` - This project overview

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Streamlit for the dashboard interface
- Pandas and Plotly for data processing and visualization

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rogo-sec-chatbot.git
   cd rogo-sec-chatbot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Dashboard

Start the metrics dashboard:

```
streamlit run metrics_dashboard_demo.py
```

### Using the Metrics System in Your Code

```python
from backend.metrics_interpreter import MetricsInterpreter, METRICS

# Initialize the interpreter
interpreter = MetricsInterpreter()

# Example financial data
company_data = {
    "is.NetRevenue": 100.0,
    "is.OperatingIncome": 20.0,
    "is.NetIncome": 15.0,
    "bs.TotalAssets": 150.0,
    "bs.TotalEquity": 70.0
}

# Calculate a metric
result = interpreter.calculate_metric("roe_pct", company_data)
if result["success"]:
    print(f"Return on Equity: {result['value']:.2f}%")
```

## Available Metrics

The system includes metrics across the following categories:

- **Income Statement**: revenue, gross_profit, operating_income, net_income, etc.
- **Balance Sheet**: cash, total_assets, total_liabilities, shareholders_equity, etc.
- **Cash Flow**: cfo, capex, free_cash_flow, etc.
- **Ratios & Margins**: gross_margin_pct, operating_margin_pct, net_margin_pct, etc.
- **Return Metrics**: roe_pct, roa_pct, roic_pct, etc.
- **Growth Metrics**: revenue_growth_pct, earnings_growth_pct, etc.
- **Valuation Metrics**: pe_ratio, ev_ebitda, price_to_book, etc.

For a complete list of metrics and their formulas, see the [METRICS.md](METRICS.md) file.

## Using the Metrics Utilities

List all available metrics:

```python
from metrics_utils import list_available_metrics

# List all metrics
all_metrics = list_available_metrics()
print(f"Found {len(all_metrics)} metrics")

# List metrics by category
income_metrics = list_available_metrics("Income Statement")
print(f"Found {len(income_metrics)} income statement metrics")
```

Search for metrics:

```python
from metrics_utils import find_metrics_by_keyword

# Find metrics related to "margin"
margin_metrics = find_metrics_by_keyword("margin")
print(f"Found {len(margin_metrics)} margin-related metrics")
```

Export metrics definitions:

```python
from metrics_utils import export_metrics_dictionary

# Export as markdown
markdown_output = export_metrics_dictionary("markdown")

# Save to file
export_metrics_dictionary("csv", "metrics_definitions.csv")
```

## Contributing

Contributions are welcome! Here are some ways you can contribute:

- Add new financial metrics to the METRICS dictionary
- Improve the accuracy of existing metric calculations
- Add support for additional companies or data sources
- Enhance the user interface and visualizations
- Fix bugs and improve error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data for demonstration purposes is based on public SEC filings
- Project structure and code patterns are designed for educational purposes