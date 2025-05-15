#!/usr/bin/env python3
"""
Example Usage of the SEC Financial Metrics System

This script demonstrates how to use the metrics system to calculate financial 
metrics for a company based on its financial data.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import logging
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Make sure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the metrics interpreter and utilities
from backend.metrics_interpreter import MetricsInterpreter, METRICS, METRIC_ALIASES
from metrics_utils import (
    list_available_metrics, 
    find_metrics_by_keyword, 
    get_metric_requirements, 
    export_metrics_dictionary
)

def example_1_basic_calculation():
    """Basic metric calculation example."""
    print("\n=== Example 1: Basic Metric Calculation ===\n")
    
    # Create a metrics interpreter
    interpreter = MetricsInterpreter()
    
    # Sample company financial data (Apple 2023)
    # We need to provide both the raw financial statement items and the derived metrics
    apple_data = {
        # Financial statement items
        "is.NetRevenue": 383.29,
        "is.CostOfRevenue": 208.02,
        "is.RD": 25.16,
        "is.SG&A": 25.36,
        "is.OperatingIncome": 109.22,
        "is.NetIncome": 97.00,
        "is.D&A": 11.49,
        "bs.TotalAssets": 355.37,
        "bs.TotalEquity": 65.02,
        "cf.CashFromOperations": 113.81,
        "cf.CapEx": -11.75,
        
        # Derived metrics that the system will use
        "revenue": 383.29,
        "cogs": 208.02,
        "gross_profit": 175.27,  # revenue - cogs
        "rnd": 25.16,
        "sga": 25.36,
        "operating_income": 109.22,
        "net_income": 97.00,
        "cfo": 113.81,
        "capex": -11.75,
        "ebit": 109.22,
        "shareholders_equity": 65.02,
        "total_assets": 355.37,
        "free_cash_flow": 125.56  # cfo - capex
    }
    
    # Calculate some basic metrics
    metrics_to_calculate = [
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income"
    ]
    
    print("Apple's Basic Income Statement Metrics (2023):")
    for metric in metrics_to_calculate:
        result = interpreter.calculate_metric(metric, apple_data)
        if result["success"]:
            print(f"{metric}: ${result['value']:.2f} billion")
        else:
            print(f"{metric}: Failed - {result.get('error', 'Unknown error')}")
    
    return interpreter, apple_data

def example_2_ratio_calculations(interpreter, apple_data):
    """Ratio metric calculation example."""
    print("\n=== Example 2: Ratio Calculations ===\n")
    
    # Calculate profit margin percentages
    ratio_metrics = [
        "gross_margin_pct",
        "operating_margin_pct",
        "net_margin_pct",
        "rd_pct",
        "roe_pct"
    ]
    
    print("Apple's Key Profitability Ratios (2023):")
    for metric in ratio_metrics:
        result = interpreter.calculate_metric(metric, apple_data)
        if result["success"]:
            print(f"{metric}: {result['value']:.2f}%")
        else:
            print(f"{metric}: Failed - {result.get('error', 'Unknown error')}")
    
    return ratio_metrics

def example_3_compound_metrics(interpreter, apple_data):
    """Compound metric calculation example."""
    print("\n=== Example 3: Compound Metrics ===\n")
    
    # Calculate metrics that require multiple inputs
    compound_metrics = [
        "free_cash_flow",
        "ebitda",
        "fcf_margin_pct"
    ]
    
    print("Apple's Compound Metrics (2023):")
    for metric in compound_metrics:
        result = interpreter.calculate_metric(metric, apple_data)
        if result["success"]:
            if metric.endswith("_pct"):
                print(f"{metric}: {result['value']:.2f}%")
            else:
                print(f"{metric}: ${result['value']:.2f} billion")
            print(f"  Formula: {result['formula']}")
            print(f"  Inputs: {', '.join(result['inputs_used'].keys())}")
        else:
            print(f"{metric}: Failed - {result.get('error', 'Unknown error')}")

def example_4_metric_aliases(interpreter, apple_data):
    """Demonstrating the use of metric aliases."""
    print("\n=== Example 4: Metric Aliases ===\n")
    
    # Using aliases for common metrics
    aliases = [
        "sales",              # alias for revenue
        "profit_margin",      # alias for net_margin_pct
        "operating_profit",   # alias for operating_income
        "r&d"                 # alias for rnd
    ]
    
    print("Using Metric Aliases:")
    for alias in aliases:
        # Get the canonical name
        canonical = METRIC_ALIASES.get(alias, alias)
        
        # Calculate the metric using the alias
        result = interpreter.calculate_metric(alias, apple_data)
        if result["success"]:
            if alias.endswith("_pct") or "margin" in alias:
                print(f"{alias} (→ {canonical}): {result['value']:.2f}%")
            else:
                print(f"{alias} (→ {canonical}): ${result['value']:.2f} billion")
        else:
            print(f"{alias}: Failed - {result.get('error', 'Unknown error')}")

def example_5_metric_search():
    """Search for metrics by keyword."""
    print("\n=== Example 5: Metric Search ===\n")
    
    # Search for metrics related to specific keywords
    keywords = ["margin", "return", "growth", "cash"]
    
    for keyword in keywords:
        results = find_metrics_by_keyword(keyword)
        print(f"Found {len(results)} metrics containing '{keyword}':")
        
        # Display the first 5 results
        df_subset = results.head(5) if len(results) > 5 else results
        for _, row in df_subset.iterrows():
            print(f"  - {row['name']}: {row['description']}")
        
        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")
        
        print()

def example_6_metric_requirements():
    """Get detailed information about metric requirements."""
    print("\n=== Example 6: Metric Requirements ===\n")
    
    metrics_to_examine = [
        "gross_profit",       # Simple metric
        "net_margin_pct",     # Ratio metric
        "ebitda",             # Compound metric
        "free_cash_flow",     # Cash flow metric
        "revenue_growth_pct"  # Growth metric requiring time series data
    ]
    
    for metric in metrics_to_examine:
        requirements = get_metric_requirements(metric)
        
        print(f"Requirements for '{metric}':")
        print(f"  Description: {requirements['description']}")
        print(f"  Formula: {requirements['formula']}")
        print(f"  Direct inputs: {', '.join(requirements['direct_inputs'])}")
        
        if requirements['income_statement_inputs']:
            print(f"  Income Statement inputs: {', '.join(requirements['income_statement_inputs'])}")
        
        if requirements['balance_sheet_inputs']:
            print(f"  Balance Sheet inputs: {', '.join(requirements['balance_sheet_inputs'])}")
        
        if requirements['cash_flow_inputs']:
            print(f"  Cash Flow inputs: {', '.join(requirements['cash_flow_inputs'])}")
        
        print()

def example_7_category_listing():
    """List metrics by category."""
    print("\n=== Example 7: Category Listing ===\n")
    
    categories = [
        "Income Statement",
        "Balance Sheet",
        "Cash Flow",
        "Ratios & Margins",
        "Return Metrics"
    ]
    
    for category in categories:
        metrics = list_available_metrics(category)
        print(f"{category} Metrics ({len(metrics)} total):")
        
        # Display the first 5 metrics in each category
        for i, (_, row) in enumerate(metrics.head(5).iterrows()):
            print(f"  {i+1}. {row['name']}: {row['description']}")
        
        if len(metrics) > 5:
            print(f"  ... and {len(metrics) - 5} more")
        
        print()

def example_8_company_comparison():
    """Compare metrics across companies."""
    print("\n=== Example 8: Company Comparison ===\n")
    
    # Financial data for multiple companies (2023)
    company_data = {
        "AAPL": {
            # Raw financial statement items
            "is.NetRevenue": 383.29,
            "is.OperatingIncome": 109.22,
            "is.NetIncome": 97.00,
            "is.RD": 25.16,
            "bs.TotalAssets": 355.37,
            "bs.TotalEquity": 65.02,
            
            # Derived metrics
            "revenue": 383.29,
            "operating_income": 109.22,
            "net_income": 97.00,
            "rnd": 25.16,
            "shareholders_equity": 65.02,
            "total_assets": 355.37
        },
        "MSFT": {
            # Raw financial statement items
            "is.NetRevenue": 211.92,
            "is.OperatingIncome": 88.52,
            "is.NetIncome": 72.36,
            "is.RD": 23.51,
            "bs.TotalAssets": 408.93,
            "bs.TotalEquity": 210.64,
            
            # Derived metrics
            "revenue": 211.92,
            "operating_income": 88.52,
            "net_income": 72.36,
            "rnd": 23.51,
            "shareholders_equity": 210.64,
            "total_assets": 408.93
        },
        "GOOG": {
            # Raw financial statement items
            "is.NetRevenue": 307.39,
            "is.OperatingIncome": 84.30,
            "is.NetIncome": 73.80,
            "is.RD": 40.23,
            "bs.TotalAssets": 410.02,
            "bs.TotalEquity": 285.56,
            
            # Derived metrics
            "revenue": 307.39,
            "operating_income": 84.30,
            "net_income": 73.80,
            "rnd": 40.23,
            "shareholders_equity": 285.56,
            "total_assets": 410.02
        },
        "META": {
            # Raw financial statement items
            "is.NetRevenue": 134.90,
            "is.OperatingIncome": 46.38,
            "is.NetIncome": 39.10,
            "is.RD": 40.65,
            "bs.TotalAssets": 196.01,
            "bs.TotalEquity": 153.02,
            
            # Derived metrics
            "revenue": 134.90,
            "operating_income": 46.38,
            "net_income": 39.10,
            "rnd": 40.65,
            "shareholders_equity": 153.02,
            "total_assets": 196.01
        }
    }
    
    # Create a metrics interpreter
    interpreter = MetricsInterpreter()
    
    # Metrics to compare
    comparison_metrics = [
        "operating_margin_pct",
        "net_margin_pct",
        "rd_pct",
        "roe_pct"
    ]
    
    # Calculate and store results
    comparison_results = {}
    for metric in comparison_metrics:
        comparison_results[metric] = {}
        
        for company, data in company_data.items():
            result = interpreter.calculate_metric(metric, data)
            if result["success"]:
                comparison_results[metric][company] = result["value"]
            else:
                comparison_results[metric][company] = None
    
    # Display results
    for metric, companies in comparison_results.items():
        print(f"{metric} Comparison:")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame({
            "Company": list(companies.keys()),
            "Value": list(companies.values())
        })
        
        # Sort by value descending
        df = df.sort_values("Value", ascending=False)
        
        # Format for display
        for i, (_, row) in enumerate(df.iterrows()):
            company = row["Company"]
            value = row["Value"]
            if value is not None:
                print(f"  {i+1}. {company}: {value:.2f}%")
            else:
                print(f"  {i+1}. {company}: N/A")
        
        print()
    
    # Create a bar chart for one of the metrics
    sample_metric = "rd_pct"
    chart_data = []
    
    for company, value in comparison_results[sample_metric].items():
        if value is not None:
            chart_data.append({"Company": company, "Value": value})
    
    if chart_data:
        chart_df = pd.DataFrame(chart_data)
        
        # Sort by value
        chart_df = chart_df.sort_values("Value", ascending=False)
        
        # Create the chart
        fig = px.bar(
            chart_df,
            x="Company",
            y="Value",
            title=f"{sample_metric} Comparison (2023)",
            labels={"Value": f"{sample_metric} (%)"}
        )
        
        # Add percentage symbol
        fig.update_layout(yaxis=dict(ticksuffix="%"))
        
        # Save the chart to a file
        fig.write_html("company_comparison.html")
        print(f"Created bar chart for {sample_metric} and saved to company_comparison.html")

def example_9_export_metrics():
    """Export metrics dictionary."""
    print("\n=== Example 9: Export Metrics ===\n")
    
    # Export metrics to different formats
    formats = ["json", "csv", "markdown"]
    
    for format_name in formats:
        filename = f"metrics_export.{format_name}"
        
        # Export to file
        export_metrics_dictionary(format_name, filename)
        print(f"Exported metrics to {filename}")
    
    print("\nSample of markdown export:")
    markdown_sample = export_metrics_dictionary("markdown")
    # Print just the first 20 lines
    print("\n".join(markdown_sample.split("\n")[:20]))
    print("...")

def main():
    """Run all examples."""
    print("SEC Financial Metrics - Usage Examples")
    print("=====================================")
    
    # Run examples
    interpreter, apple_data = example_1_basic_calculation()
    example_2_ratio_calculations(interpreter, apple_data)
    example_3_compound_metrics(interpreter, apple_data)
    example_4_metric_aliases(interpreter, apple_data)
    example_5_metric_search()
    example_6_metric_requirements()
    example_7_category_listing()
    example_8_company_comparison()
    example_9_export_metrics()
    
    print("\nAll examples completed!")

if __name__ == "__main__":
    main() 