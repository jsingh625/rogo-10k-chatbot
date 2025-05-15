#!/usr/bin/env python3
"""
Metrics Utilities for SEC filings data.

This module provides utility functions to work with the metrics definitions
and calculations from the metrics_interpreter module.
"""

import logging
import sys
import pandas as pd
import json
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the metrics interpreter
from backend.metrics_interpreter import METRICS, METRIC_ALIASES, MetricsInterpreter

def list_available_metrics(category: Optional[str] = None) -> pd.DataFrame:
    """
    List all available metrics with descriptions, optionally filtered by category.
    
    Args:
        category: Optional category to filter metrics (e.g., 'income_statement', 'balance_sheet', etc.)
        
    Returns:
        DataFrame with metrics information
    """
    metrics_data = []
    
    for name, info in METRICS.items():
        # Determine category based on the metric name or formula
        metric_category = _determine_category(name, info)
        
        # Filter by category if specified
        if category and category.lower() != metric_category.lower():
            continue
            
        metrics_data.append({
            "name": name,
            "description": info["desc"],
            "formula": info["formula"],
            "category": metric_category,
            "is_ratio": name.endswith("_pct") or "ratio" in name.lower() or "margin" in name.lower(),
            "inputs": ", ".join(info["inputs"])
        })
    
    # Convert to DataFrame and sort
    df = pd.DataFrame(metrics_data)
    if not df.empty:
        df = df.sort_values(["category", "name"])
    
    return df

def _determine_category(name: str, info: Dict[str, Any]) -> str:
    """
    Determine the category of a metric based on its name and inputs.
    
    Args:
        name: Metric name
        info: Metric information dictionary
        
    Returns:
        Category as a string
    """
    if any(inp.startswith("is.") for inp in info["inputs"]) or name in [
        "revenue", "cogs", "gross_profit", "rnd", "sga", "operating_income",
        "ebit", "interest_expense", "ebt", "tax_expense", "net_income"
    ]:
        return "Income Statement"
    
    elif any(inp.startswith("bs.") for inp in info["inputs"]) or name in [
        "cash", "short_term_investments", "accounts_receivable", "inventory",
        "total_assets", "accounts_payable", "total_liabilities", "shareholders_equity"
    ]:
        return "Balance Sheet"
    
    elif any(inp.startswith("cf.") for inp in info["inputs"]) or name in [
        "cfo", "capex", "free_cash_flow", "cfi", "cff"
    ]:
        return "Cash Flow"
    
    elif name.endswith("_pct") or "margin" in name or "ratio" in name:
        return "Ratios & Margins"
    
    elif "growth" in name:
        return "Growth Metrics"
    
    elif "per_share" in name or name in ["eps_basic", "eps_diluted"]:
        return "Per Share Metrics"
    
    elif "return" in name or name in ["roa_pct", "roe_pct", "roce_pct"]:
        return "Return Metrics"
    
    else:
        return "Other Metrics"

def calculate_metric_for_company(company_data: Dict[str, Any], metric_name: str) -> Dict[str, Any]:
    """
    Calculate a specific metric for a company based on its financial data.
    
    Args:
        company_data: Dictionary of company financial data
        metric_name: Name of the metric to calculate
        
    Returns:
        Dictionary with calculation result and details
    """
    interpreter = MetricsInterpreter()
    return interpreter.calculate_metric(metric_name, company_data)

def find_metrics_by_keyword(keyword: str) -> pd.DataFrame:
    """
    Find metrics that match a keyword in their name or description.
    
    Args:
        keyword: Keyword to search for
        
    Returns:
        DataFrame with matching metrics
    """
    keyword = keyword.lower()
    metrics_data = []
    
    for name, info in METRICS.items():
        if (keyword in name.lower() or 
            keyword in info["desc"].lower() or
            any(keyword in input_name.lower() for input_name in info["inputs"])):
            
            # Determine category
            metric_category = _determine_category(name, info)
            
            metrics_data.append({
                "name": name,
                "description": info["desc"],
                "formula": info["formula"],
                "category": metric_category,
                "is_ratio": name.endswith("_pct") or "ratio" in name.lower() or "margin" in name.lower(),
                "inputs": ", ".join(info["inputs"])
            })
    
    # Convert to DataFrame and sort
    df = pd.DataFrame(metrics_data)
    if not df.empty:
        df = df.sort_values(["category", "name"])
    
    return df

def get_metric_requirements(metric_name: str) -> Dict[str, Any]:
    """
    Get detailed information about what data is required to calculate a metric.
    
    Args:
        metric_name: Name of the metric
        
    Returns:
        Dictionary with requirements information
    """
    # Resolve alias if needed
    if metric_name in METRIC_ALIASES:
        metric_name = METRIC_ALIASES[metric_name]
    
    if metric_name not in METRICS:
        return {"error": f"Unknown metric: {metric_name}"}
    
    info = METRICS[metric_name]
    
    # Collect all required inputs, including nested inputs
    all_inputs = set(info["inputs"])
    processed_metrics = set()
    
    def collect_inputs(metric):
        if metric in processed_metrics or metric not in METRICS:
            return
        
        processed_metrics.add(metric)
        
        for inp in METRICS[metric]["inputs"]:
            all_inputs.add(inp)
            
            # If this input is another metric (not a direct financial statement item)
            if not inp.startswith(("is.", "bs.", "cf.")) and inp in METRICS:
                collect_inputs(inp)
    
    # Start with the requested metric
    for input_metric in info["inputs"]:
        if not input_metric.startswith(("is.", "bs.", "cf.")) and input_metric in METRICS:
            collect_inputs(input_metric)
    
    # Categorize inputs
    income_statement_inputs = [inp for inp in all_inputs if inp.startswith("is.")]
    balance_sheet_inputs = [inp for inp in all_inputs if inp.startswith("bs.")]
    cash_flow_inputs = [inp for inp in all_inputs if inp.startswith("cf.")]
    derived_inputs = [inp for inp in all_inputs if not inp.startswith(("is.", "bs.", "cf."))]
    
    return {
        "metric": metric_name,
        "description": info["desc"],
        "formula": info["formula"],
        "direct_inputs": info["inputs"],
        "all_required_inputs": list(all_inputs),
        "income_statement_inputs": income_statement_inputs,
        "balance_sheet_inputs": balance_sheet_inputs,
        "cash_flow_inputs": cash_flow_inputs,
        "derived_inputs": derived_inputs
    }

def export_metrics_dictionary(output_format: str = "json", output_file: Optional[str] = None) -> Union[str, None]:
    """
    Export the metrics dictionary to various formats.
    
    Args:
        output_format: Format to export to ("json", "csv", "markdown")
        output_file: Optional file to write to
        
    Returns:
        Formatted string if output_file is None, otherwise None
    """
    metrics_df = list_available_metrics()
    
    if output_format.lower() == "json":
        result = metrics_df.to_json(orient="records", indent=2)
        
    elif output_format.lower() == "csv":
        result = metrics_df.to_csv(index=False)
        
    elif output_format.lower() == "markdown":
        result = "# Financial Metrics Dictionary\n\n"
        
        # Group by category
        for category, group in metrics_df.groupby("category"):
            result += f"## {category}\n\n"
            result += "| Metric | Description | Formula | Inputs |\n"
            result += "|--------|-------------|---------|--------|\n"
            
            for _, row in group.iterrows():
                formula = row["formula"].replace("|", "\\|")  # Escape pipe characters in markdown tables
                result += f"| `{row['name']}` | {row['description']} | `{formula}` | {row['inputs']} |\n"
            
            result += "\n"
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
    
    # Write to file if specified
    if output_file:
        with open(output_file, "w") as f:
            f.write(result)
        return None
    
    return result

if __name__ == "__main__":
    # Simple command-line interface
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            df = list_available_metrics(category)
            print(df.to_string())
            
        elif command == "search":
            if len(sys.argv) > 2:
                keyword = sys.argv[2]
                df = find_metrics_by_keyword(keyword)
                print(f"Found {len(df)} metrics matching '{keyword}':")
                print(df.to_string())
            else:
                print("Please provide a search keyword")
                
        elif command == "export":
            output_format = sys.argv[2] if len(sys.argv) > 2 else "json"
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            result = export_metrics_dictionary(output_format, output_file)
            if result:
                print(result)
        
        elif command == "info":
            if len(sys.argv) > 2:
                metric_name = sys.argv[2]
                info = get_metric_requirements(metric_name)
                print(json.dumps(info, indent=2))
            else:
                print("Please provide a metric name")
        
        else:
            print(f"Unknown command: {command}")
    else:
        print("Available commands:")
        print("  list [category]   - List all metrics, optionally filtered by category")
        print("  search <keyword>  - Search for metrics by keyword")
        print("  export [format] [file] - Export metrics dictionary (json, csv, markdown)")
        print("  info <metric>     - Get detailed information about a metric") 