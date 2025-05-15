#!/usr/bin/env python3
"""
Metrics Dashboard Demo

A simple demonstration of how to use the metrics system to calculate 
and visualize financial metrics for selected companies.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the metrics utilities and interpreter
from metrics_utils import list_available_metrics, find_metrics_by_keyword
from backend.metrics_interpreter import MetricsInterpreter, METRICS

# Sample financial data for demonstration purposes
sample_data = {
    "AAPL": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 383.29,
            "is.CostOfRevenue": 208.02,
            "is.RD": 25.16,
            "is.SG&A": 25.36,
            "is.OperatingIncome": 109.22,
            "is.D&A": 11.49,
            "is.InterestExpense": -0.92,
            "is.IncomeTax": 18.10,
            "is.NetIncome": 97.00,
            "bs.CashAndEquivalents": 29.97,
            "bs.ShortTermInvestments": 31.58,
            "bs.AccountsReceivable": 23.52,
            "bs.Inventory": 6.33,
            "bs.TotalCurrentAssets": 141.62,
            "bs.PP&E": 42.39,
            "bs.TotalAssets": 355.37,
            "bs.AccountsPayable": 62.31,
            "bs.ShortTermDebt": 14.76,
            "bs.TotalCurrentLiabilities": 127.71,
            "bs.LongTermDebt": 95.28,
            "bs.TotalLiabilities": 290.35,
            "bs.TotalEquity": 65.02,
            "cf.CashFromOperations": 113.81,
            "cf.CapEx": -11.75,
            "cf.CashFromInvesting": -7.70,
            "cf.CashFromFinancing": -104.19,
            
            # Derived metrics that need to be pre-calculated
            "revenue": 383.29,
            "cogs": 208.02,
            "gross_profit": 175.27,
            "rnd": 25.16,
            "sga": 25.36,
            "operating_income": 109.22,
            "ebit": 109.22,
            "ebitda": 120.71,  # operating_income + is.D&A
            "net_income": 97.00,
            "shareholders_equity": 65.02,
            "total_assets": 355.37,
            "cfo": 113.81,
            "capex": -11.75,
            "free_cash_flow": 125.56
        },
        "2022": {
            # Financial statement items
            "is.NetRevenue": 394.33,
            "is.CostOfRevenue": 223.55,
            "is.RD": 22.10,
            "is.SG&A": 24.25,
            "is.OperatingIncome": 119.44,
            "is.D&A": 11.10,
            "is.InterestExpense": -0.86,
            "is.IncomeTax": 19.30,
            "is.NetIncome": 99.80,
            "bs.CashAndEquivalents": 23.65,
            "bs.ShortTermInvestments": 24.66,
            "bs.AccountsReceivable": 28.18,
            "bs.Inventory": 4.95,
            "bs.TotalCurrentAssets": 135.41,
            "bs.PP&E": 39.44,
            "bs.TotalAssets": 352.76,
            "bs.AccountsPayable": 64.12,
            "bs.ShortTermDebt": 11.13,
            "bs.TotalCurrentLiabilities": 153.00,
            "bs.LongTermDebt": 98.96,
            "bs.TotalLiabilities": 302.08,
            "bs.TotalEquity": 50.67,
            "cf.CashFromOperations": 122.15,
            "cf.CapEx": -10.71,
            "cf.CashFromInvesting": -22.83,
            "cf.CashFromFinancing": -110.75,
            
            # Derived metrics
            "revenue": 394.33,
            "cogs": 223.55,
            "gross_profit": 170.78,
            "rnd": 22.10,
            "sga": 24.25,
            "operating_income": 119.44,
            "ebit": 119.44,
            "ebitda": 130.54,  # operating_income + is.D&A
            "net_income": 99.80,
            "shareholders_equity": 50.67,
            "total_assets": 352.76,
            "cfo": 122.15,
            "capex": -10.71,
            "free_cash_flow": 132.86
        }
    },
    "MSFT": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 211.92,
            "is.CostOfRevenue": 70.76,
            "is.RD": 23.51,
            "is.SG&A": 31.00,
            "is.OperatingIncome": 88.52,
            "is.D&A": 15.46,
            "is.InterestExpense": -2.31,
            "is.IncomeTax": 10.43,
            "is.NetIncome": 72.36,
            "bs.CashAndEquivalents": 34.70,
            "bs.ShortTermInvestments": 76.58,
            "bs.AccountsReceivable": 44.26,
            "bs.Inventory": 3.71,
            "bs.TotalCurrentAssets": 169.69,
            "bs.PP&E": 87.34,
            "bs.TotalAssets": 408.93,
            "bs.AccountsPayable": 20.73,
            "bs.ShortTermDebt": 5.24,
            "bs.TotalCurrentLiabilities": 91.46,
            "bs.LongTermDebt": 41.98,
            "bs.TotalLiabilities": 198.30,
            "bs.TotalEquity": 210.64,
            "cf.CashFromOperations": 87.89,
            "cf.CapEx": -28.42,
            "cf.CashFromInvesting": -33.06,
            "cf.CashFromFinancing": -36.55,
            
            # Derived metrics
            "revenue": 211.92,
            "cogs": 70.76,
            "gross_profit": 141.16,
            "rnd": 23.51,
            "sga": 31.00,
            "operating_income": 88.52,
            "ebit": 88.52,
            "ebitda": 103.98,  # operating_income + is.D&A
            "net_income": 72.36,
            "shareholders_equity": 210.64,
            "total_assets": 408.93,
            "cfo": 87.89,
            "capex": -28.42,
            "free_cash_flow": 116.31
        },
        "2022": {
            # Financial statement items
            "is.NetRevenue": 198.27,
            "is.CostOfRevenue": 61.30,
            "is.RD": 21.53,
            "is.SG&A": 28.32,
            "is.OperatingIncome": 83.38,
            "is.D&A": 14.46,
            "is.InterestExpense": -2.21,
            "is.IncomeTax": 10.20,
            "is.NetIncome": 72.74,
            "bs.CashAndEquivalents": 13.93,
            "bs.ShortTermInvestments": 88.86,
            "bs.AccountsReceivable": 44.26,
            "bs.Inventory": 3.33,
            "bs.TotalCurrentAssets": 169.69,
            "bs.PP&E": 74.64,
            "bs.TotalAssets": 364.84,
            "bs.AccountsPayable": 19.55,
            "bs.ShortTermDebt": 2.75,
            "bs.TotalCurrentLiabilities": 82.90,
            "bs.LongTermDebt": 47.03,
            "bs.TotalLiabilities": 188.30,
            "bs.TotalEquity": 166.54,
            "cf.CashFromOperations": 89.03,
            "cf.CapEx": -23.89,
            "cf.CashFromInvesting": -30.22,
            "cf.CashFromFinancing": -40.15,
            
            # Derived metrics
            "revenue": 198.27,
            "cogs": 61.30,
            "gross_profit": 136.97,
            "rnd": 21.53,
            "sga": 28.32,
            "operating_income": 83.38,
            "ebit": 83.38,
            "ebitda": 97.84,  # operating_income + is.D&A
            "net_income": 72.74,
            "shareholders_equity": 166.54,
            "total_assets": 364.84,
            "cfo": 89.03,
            "capex": -23.89,
            "free_cash_flow": 112.92
        }
    },
    "GOOG": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 307.39,
            "is.CostOfRevenue": 132.59,
            "is.RD": 40.23,
            "is.SG&A": 44.29,
            "is.OperatingIncome": 84.30,
            "is.D&A": 16.94,
            "is.InterestExpense": 0.88,
            "is.IncomeTax": 10.52,
            "is.NetIncome": 73.80,
            "bs.CashAndEquivalents": 24.07,
            "bs.ShortTermInvestments": 90.57,
            "bs.TotalCurrentAssets": 169.24,
            "bs.PP&E": 124.29,
            "bs.TotalAssets": 410.02,
            "bs.TotalCurrentLiabilities": 64.05,
            "bs.LongTermDebt": 13.24,
            "bs.TotalLiabilities": 124.46,
            "bs.TotalEquity": 285.56,
            "cf.CashFromOperations": 91.58,
            "cf.CapEx": -31.50,
            "cf.CashFromInvesting": -37.42,
            "cf.CashFromFinancing": -46.95,
            
            # Derived metrics
            "revenue": 307.39,
            "cogs": 132.59,
            "gross_profit": 174.80,
            "rnd": 40.23, 
            "sga": 44.29,
            "operating_income": 84.30,
            "ebit": 84.30,
            "ebitda": 101.24,  # operating_income + is.D&A
            "net_income": 73.80,
            "shareholders_equity": 285.56,
            "total_assets": 410.02,
            "cfo": 91.58,
            "capex": -31.50,
            "free_cash_flow": 123.08
        }
    },
    "META": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 134.90,
            "is.CostOfRevenue": 28.36,
            "is.RD": 40.65,
            "is.SG&A": 24.35,
            "is.OperatingIncome": 46.38,
            "is.D&A": 10.25,
            "is.InterestExpense": 0.21,
            "is.IncomeTax": 7.27,
            "is.NetIncome": 39.10,
            "bs.CashAndEquivalents": 39.53,
            "bs.ShortTermInvestments": 40.01,
            "bs.TotalCurrentAssets": 92.28,
            "bs.PP&E": 73.13,
            "bs.TotalAssets": 196.01,
            "bs.TotalCurrentLiabilities": 25.10,
            "bs.LongTermDebt": 18.39,
            "bs.TotalLiabilities": 42.99,
            "bs.TotalEquity": 153.02,
            "cf.CashFromOperations": 67.84,
            "cf.CapEx": -27.83,
            "cf.CashFromInvesting": -32.53,
            "cf.CashFromFinancing": -6.18,
            
            # Derived metrics
            "revenue": 134.90,
            "cogs": 28.36,
            "gross_profit": 106.54,
            "rnd": 40.65,
            "sga": 24.35,
            "operating_income": 46.38,
            "ebit": 46.38,
            "ebitda": 56.63,  # operating_income + is.D&A
            "net_income": 39.10,
            "shareholders_equity": 153.02,
            "total_assets": 196.01,
            "cfo": 67.84,
            "capex": -27.83,
            "free_cash_flow": 95.67
        }
    },
    "AMZN": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 574.78,
            "is.CostOfRevenue": 321.74,
            "is.RD": 73.81,
            "is.SG&A": 116.12,
            "is.OperatingIncome": 36.85,
            "is.D&A": 51.33,
            "is.InterestExpense": -2.75,
            "is.IncomeTax": 6.58,
            "is.NetIncome": 30.43,
            "bs.CashAndEquivalents": 73.88,
            "bs.ShortTermInvestments": 15.01,
            "bs.TotalCurrentAssets": 146.39,
            "bs.PP&E": 186.84,
            "bs.TotalAssets": 527.55,
            "bs.TotalCurrentLiabilities": 163.95,
            "bs.LongTermDebt": 65.04,
            "bs.TotalLiabilities": 307.05,
            "bs.TotalEquity": 220.50,
            "cf.CashFromOperations": 84.90,
            "cf.CapEx": -48.75,
            "cf.CashFromInvesting": -46.13,
            "cf.CashFromFinancing": -8.56,
            
            # Derived metrics
            "revenue": 574.78,
            "cogs": 321.74,
            "gross_profit": 253.04,
            "rnd": 73.81,
            "sga": 116.12,
            "operating_income": 36.85,
            "ebit": 36.85,
            "ebitda": 88.18,  # operating_income + is.D&A
            "net_income": 30.43,
            "shareholders_equity": 220.50,
            "total_assets": 527.55,
            "cfo": 84.90,
            "capex": -48.75,
            "free_cash_flow": 133.65
        }
    },
    "NVDA": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 60.92,
            "is.CostOfRevenue": 18.68,
            "is.RD": 7.05,
            "is.SG&A": 3.85,
            "is.OperatingIncome": 31.33,
            "is.D&A": 1.03,
            "is.InterestExpense": 0.24,
            "is.IncomeTax": 2.79,
            "is.NetIncome": 29.76,
            "bs.CashAndEquivalents": 4.88,
            "bs.ShortTermInvestments": 22.55,
            "bs.TotalCurrentAssets": 45.93,
            "bs.PP&E": 5.13,
            "bs.TotalAssets": 65.22,
            "bs.TotalCurrentLiabilities": 9.44,
            "bs.LongTermDebt": 9.70,
            "bs.TotalLiabilities": 22.66,
            "bs.TotalEquity": 42.56,
            "cf.CashFromOperations": 29.55,
            "cf.CapEx": -2.20,
            "cf.CashFromInvesting": -29.97,
            "cf.CashFromFinancing": -7.95,
            
            # Derived metrics
            "revenue": 60.92,
            "cogs": 18.68,
            "gross_profit": 42.24,
            "rnd": 7.05,
            "sga": 3.85,
            "operating_income": 31.33,
            "ebit": 31.33,
            "ebitda": 32.36,  # operating_income + is.D&A
            "net_income": 29.76,
            "shareholders_equity": 42.56,
            "total_assets": 65.22,
            "cfo": 29.55,
            "capex": -2.20,
            "free_cash_flow": 31.75
        }
    },
    "TSLA": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 96.77,
            "is.CostOfRevenue": 75.54,
            "is.RD": 3.52,
            "is.SG&A": 5.24,
            "is.OperatingIncome": 12.43,
            "is.D&A": 4.59,
            "is.InterestExpense": 0.39,
            "is.IncomeTax": 1.65,
            "is.NetIncome": 14.99,
            "bs.CashAndEquivalents": 29.10,
            "bs.ShortTermInvestments": 14.66,
            "bs.TotalCurrentAssets": 47.54,
            "bs.PP&E": 46.21,
            "bs.TotalAssets": 120.32,
            "bs.TotalCurrentLiabilities": 26.77,
            "bs.LongTermDebt": 3.69,
            "bs.TotalLiabilities": 41.47,
            "bs.TotalEquity": 78.85,
            "cf.CashFromOperations": 13.26,
            "cf.CapEx": -8.91,
            "cf.CashFromInvesting": -10.91,
            "cf.CashFromFinancing": 0.25,
            
            # Derived metrics
            "revenue": 96.77,
            "cogs": 75.54,
            "gross_profit": 21.23,
            "rnd": 3.52,
            "sga": 5.24,
            "operating_income": 12.43,
            "ebit": 12.43,
            "ebitda": 17.02,  # operating_income + is.D&A
            "net_income": 14.99,
            "shareholders_equity": 78.85,
            "total_assets": 120.32,
            "cfo": 13.26,
            "capex": -8.91,
            "free_cash_flow": 22.17
        }
    },
    "AVGO": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 33.20,
            "is.CostOfRevenue": 11.51,
            "is.RD": 5.22,
            "is.SG&A": 1.45,
            "is.OperatingIncome": 8.85,
            "is.D&A": 6.17,
            "is.InterestExpense": -1.96,
            "is.IncomeTax": 0.76,
            "is.NetIncome": 11.50,
            "bs.CashAndEquivalents": 12.13,
            "bs.TotalCurrentAssets": 19.52,
            "bs.PP&E": 5.41,
            "bs.TotalAssets": 144.46,
            "bs.TotalCurrentLiabilities": 10.85,
            "bs.LongTermDebt": 39.27,
            "bs.TotalLiabilities": 73.97,
            "bs.TotalEquity": 70.49,
            "cf.CashFromOperations": 17.38,
            "cf.CapEx": -0.51,
            "cf.CashFromInvesting": -62.64,
            "cf.CashFromFinancing": 57.16,
            
            # Derived metrics
            "revenue": 33.20,
            "cogs": 11.51,
            "gross_profit": 21.69,
            "rnd": 5.22,
            "sga": 1.45,
            "operating_income": 8.85,
            "ebit": 8.85,
            "ebitda": 15.02,  # operating_income + is.D&A
            "net_income": 11.50,
            "shareholders_equity": 70.49,
            "total_assets": 144.46,
            "cfo": 17.38,
            "capex": -0.51,
            "free_cash_flow": 17.89
        }
    },
    "BRK-B": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 364.51,
            "is.CostOfRevenue": 297.30,
            "is.OperatingIncome": 37.35,
            "is.D&A": 10.53,
            "is.IncomeTax": 6.27,
            "is.NetIncome": 96.22,
            "bs.CashAndEquivalents": 173.66,
            "bs.TotalCurrentAssets": 337.19,
            "bs.PP&E": 165.65,
            "bs.TotalAssets": 1099.30,
            "bs.TotalCurrentLiabilities": 133.65,
            "bs.LongTermDebt": 122.35,
            "bs.TotalLiabilities": 469.38,
            "bs.TotalEquity": 629.92,
            "cf.CashFromOperations": 45.02,
            "cf.CapEx": -17.60,
            "cf.CashFromInvesting": 4.71,
            "cf.CashFromFinancing": -3.61,
            
            # Derived metrics
            "revenue": 364.51,
            "cogs": 297.30,
            "gross_profit": 67.21,
            "operating_income": 37.35,
            "ebit": 37.35,
            "ebitda": 47.88,  # operating_income + is.D&A
            "net_income": 96.22,
            "shareholders_equity": 629.92,
            "total_assets": 1099.30,
            "cfo": 45.02,
            "capex": -17.60,
            "free_cash_flow": 62.62
        }
    },
    "JPM": {
        "2023": {
            # Financial statement items
            "is.NetRevenue": 157.04,
            "is.OperatingIncome": 61.28,
            "is.D&A": 8.65,
            "is.IncomeTax": 13.69,
            "is.NetIncome": 49.55,
            "bs.CashAndEquivalents": 529.15,
            "bs.TotalAssets": 3870.35,
            "bs.TotalLiabilities": 3517.80,
            "bs.TotalEquity": 352.55,
            "cf.CashFromOperations": 21.34,
            "cf.CapEx": -2.35,
            
            # Derived metrics
            "revenue": 157.04,
            "operating_income": 61.28,
            "ebit": 61.28,
            "ebitda": 69.93,  # operating_income + is.D&A
            "net_income": 49.55,
            "shareholders_equity": 352.55,
            "total_assets": 3870.35,
            "cfo": 21.34,
            "capex": -2.35,
            "free_cash_flow": 23.69
        }
    }
}

# Calculate derived metrics
def calculate_all_metrics(company_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Calculate all available metrics for a company's financial data."""
    interpreter = MetricsInterpreter()
    derived_data = {}
    
    # First calculate non-time-series metrics
    for year, data in company_data.items():
        derived_data[year] = {}
        
        # Copy the source data
        for key, value in data.items():
            derived_data[year][key] = value
        
        # First pass - calculate basic derived metrics if they don't exist
        if "revenue" not in derived_data[year] and "is.NetRevenue" in derived_data[year]:
            derived_data[year]["revenue"] = derived_data[year]["is.NetRevenue"]
            
        if "cogs" not in derived_data[year] and "is.CostOfRevenue" in derived_data[year]:
            derived_data[year]["cogs"] = derived_data[year]["is.CostOfRevenue"]
            
        if "operating_income" not in derived_data[year] and "is.OperatingIncome" in derived_data[year]:
            derived_data[year]["operating_income"] = derived_data[year]["is.OperatingIncome"]
            
        if "ebit" not in derived_data[year] and "operating_income" in derived_data[year]:
            derived_data[year]["ebit"] = derived_data[year]["operating_income"]
            
        if "ebitda" not in derived_data[year] and "operating_income" in derived_data[year] and "is.D&A" in derived_data[year]:
            derived_data[year]["ebitda"] = derived_data[year]["operating_income"] + derived_data[year]["is.D&A"]
            
        if "net_income" not in derived_data[year] and "is.NetIncome" in derived_data[year]:
            derived_data[year]["net_income"] = derived_data[year]["is.NetIncome"]
            
        if "rnd" not in derived_data[year] and "is.RD" in derived_data[year]:
            derived_data[year]["rnd"] = derived_data[year]["is.RD"]
            
        if "sga" not in derived_data[year] and "is.SG&A" in derived_data[year]:
            derived_data[year]["sga"] = derived_data[year]["is.SG&A"]
            
        if "shareholders_equity" not in derived_data[year] and "bs.TotalEquity" in derived_data[year]:
            derived_data[year]["shareholders_equity"] = derived_data[year]["bs.TotalEquity"]
            
        if "total_assets" not in derived_data[year] and "bs.TotalAssets" in derived_data[year]:
            derived_data[year]["total_assets"] = derived_data[year]["bs.TotalAssets"]
            
        if "cfo" not in derived_data[year] and "cf.CashFromOperations" in derived_data[year]:
            derived_data[year]["cfo"] = derived_data[year]["cf.CashFromOperations"]
            
        if "capex" not in derived_data[year] and "cf.CapEx" in derived_data[year]:
            derived_data[year]["capex"] = derived_data[year]["cf.CapEx"]
        
        # Second pass - calculate compound metrics
        if "gross_profit" not in derived_data[year] and "revenue" in derived_data[year] and "cogs" in derived_data[year]:
            derived_data[year]["gross_profit"] = derived_data[year]["revenue"] - derived_data[year]["cogs"]
            
        if "free_cash_flow" not in derived_data[year] and "cfo" in derived_data[year] and "capex" in derived_data[year]:
            derived_data[year]["free_cash_flow"] = derived_data[year]["cfo"] - derived_data[year]["capex"]
        
        # Calculate all remaining metrics
        for metric_name in METRICS:
            # Skip time-series metrics that require data from multiple periods
            if "_t" in METRICS[metric_name]["formula"]:
                continue
                
            # Skip if metric is already calculated
            if metric_name in derived_data[year]:
                continue
                
            # Calculate the metric
            result = interpreter.calculate_metric(metric_name, derived_data[year])
            if result["success"]:
                derived_data[year][metric_name] = result["value"]
    
    # Now calculate metrics that require multiple periods (e.g., growth rates)
    years = sorted(derived_data.keys())
    for i, current_year in enumerate(years):
        if i > 0:  # Need a previous year for comparison
            prev_year = years[i-1]
            
            # Create a dataset with current and previous year values
            time_series_data = {}
            
            # Add current year metrics with _t suffix
            for metric, value in derived_data[current_year].items():
                time_series_data[f"{metric}_t"] = value
                
            # Add previous year metrics with _t-1 suffix
            for metric, value in derived_data[prev_year].items():
                time_series_data[f"{metric}_t-1"] = value
            
            # Calculate time-series metrics
            for metric_name, metric_info in METRICS.items():
                if "_t" in metric_info["formula"] and metric_name not in derived_data[current_year]:
                    result = interpreter.calculate_metric(metric_name, time_series_data)
                    if result["success"]:
                        derived_data[current_year][metric_name] = result["value"]
    
    return derived_data

# Pre-calculate metrics for demo companies
company_metrics = {}
for company, yearly_data in sample_data.items():
    company_metrics[company] = calculate_all_metrics(yearly_data)

# Set up the Streamlit app
def main():
    st.set_page_config(
        page_title="Financial Metrics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Financial Metrics Dashboard")
    st.markdown("""
    This dashboard demonstrates the use of the metrics system to calculate and visualize financial metrics.
    The data shown is for demonstration purposes only.
    """)
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    
    # Company selector
    companies = list(sample_data.keys())
    selected_companies = st.sidebar.multiselect(
        "Select Companies", 
        companies,
        default=companies[:2]
    )
    
    # Year selector
    available_years = sorted(list(sample_data[companies[0]].keys()), reverse=True)
    selected_years = st.sidebar.multiselect(
        "Select Years",
        available_years,
        default=available_years[:2]
    )
    
    # Metric category selector
    metric_categories = [
        "Income Statement", 
        "Balance Sheet",
        "Cash Flow",
        "Ratios & Margins",
        "Growth Metrics",
        "Return Metrics"
    ]
    selected_category = st.sidebar.selectbox(
        "Select Metric Category",
        metric_categories
    )
    
    # Get metrics for the selected category
    metrics_df = list_available_metrics(selected_category)
    metric_options = metrics_df["name"].tolist()
    
    # Metric selector
    selected_metrics = st.sidebar.multiselect(
        "Select Metrics",
        metric_options,
        default=metric_options[:3] if metric_options else []
    )
    
    # Search for metrics
    search_keyword = st.sidebar.text_input("Search Metrics")
    if search_keyword:
        search_results = find_metrics_by_keyword(search_keyword)
        if not search_results.empty:
            st.sidebar.subheader(f"Found {len(search_results)} metrics:")
            for _, row in search_results.iterrows():
                if st.sidebar.checkbox(f"{row['name']} - {row['description']}", key=f"search_{row['name']}"):
                    if row['name'] not in selected_metrics:
                        selected_metrics.append(row['name'])
    
    # Main content
    if not selected_companies or not selected_years or not selected_metrics:
        st.info("Please select companies, years, and metrics to view the dashboard.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Table View", "Company Comparison", "Trend Analysis"])
    
    # Table View Tab
    with tab1:
        st.subheader("Financial Metrics Table")
        
        # Prepare data for display
        table_data = []
        
        for company in selected_companies:
            for year in selected_years:
                if year in company_metrics[company]:
                    row_data = {"Company": company, "Year": year}
                    
                    for metric in selected_metrics:
                        if metric in company_metrics[company][year]:
                            value = company_metrics[company][year][metric]
                            
                            # Format based on metric type
                            if metric.endswith("_pct") or "margin" in metric.lower() or "ratio" in metric.lower():
                                row_data[metric] = f"{value:.2f}%"
                            else:
                                row_data[metric] = f"${value:.2f}B"
                        else:
                            row_data[metric] = "N/A"
                    
                    table_data.append(row_data)
        
        if table_data:
            table_df = pd.DataFrame(table_data)
            st.dataframe(table_df, use_container_width=True)
        else:
            st.info("No data available for the selected options.")
    
    # Company Comparison Tab
    with tab2:
        st.subheader("Company Comparison")
        
        # Select year for comparison
        comparison_year = st.selectbox("Select Year for Comparison", selected_years)
        
        # Prepare data for comparison charts
        for metric in selected_metrics:
            chart_data = []
            
            for company in selected_companies:
                if comparison_year in company_metrics[company] and metric in company_metrics[company][comparison_year]:
                    value = company_metrics[company][comparison_year][metric]
                    chart_data.append({"Company": company, "Value": value})
            
            if chart_data:
                chart_df = pd.DataFrame(chart_data)
                
                # Determine if this is a percentage metric
                is_percentage = metric.endswith("_pct") or "margin" in metric.lower() or "ratio" in metric.lower()
                
                # Create chart
                fig = px.bar(
                    chart_df,
                    x="Company",
                    y="Value",
                    title=f"{metric} Comparison ({comparison_year})",
                    labels={"Value": f"{metric} ({'%' if is_percentage else '$ billions'})"}
                )
                
                # Add percentage symbol for ratio metrics
                if is_percentage:
                    fig.update_layout(yaxis=dict(ticksuffix="%"))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add metric description
                if metric in METRICS:
                    st.markdown(f"**{metric}**: {METRICS[metric]['desc']}")
                    st.markdown(f"**Formula**: `{METRICS[metric]['formula']}`")
    
    # Trend Analysis Tab
    with tab3:
        st.subheader("Trend Analysis")
        
        # Select company for trend analysis
        trend_company = st.selectbox("Select Company for Trend Analysis", selected_companies)
        
        # Prepare data for trend charts
        for metric in selected_metrics:
            chart_data = []
            
            for year in sorted(selected_years):
                if year in company_metrics[trend_company] and metric in company_metrics[trend_company][year]:
                    value = company_metrics[trend_company][year][metric]
                    chart_data.append({"Year": year, "Value": value})
            
            if len(chart_data) > 1:  # Need at least two points for a trend
                chart_df = pd.DataFrame(chart_data)
                
                # Determine if this is a percentage metric
                is_percentage = metric.endswith("_pct") or "margin" in metric.lower() or "ratio" in metric.lower()
                
                # Create chart with integer x-axis ticks for years
                fig = px.line(
                    chart_df,
                    x="Year",
                    y="Value",
                    title=f"{metric} Trend for {trend_company}",
                    labels={"Value": f"{metric} ({'%' if is_percentage else '$ billions'})"},
                    markers=True
                )
                
                # Configure x-axis to show only whole years as integers
                fig.update_xaxes(
                    tickmode='array',
                    tickvals=chart_df["Year"].tolist(),
                    ticktext=chart_df["Year"].tolist(),
                    type='category'  # Use category type to ensure exact values
                )
                
                # Add percentage symbol for ratio metrics
                if is_percentage:
                    fig.update_layout(yaxis=dict(ticksuffix="%"))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display year-over-year changes
                if len(chart_data) > 1:
                    st.subheader("Year-over-Year Changes")
                    
                    # Calculate changes
                    yoy_data = []
                    prev_value = None
                    
                    for i, row in enumerate(chart_data):
                        if i > 0:
                            year = row["Year"]
                            value = row["Value"]
                            change = value - prev_value
                            pct_change = (change / prev_value) * 100 if prev_value != 0 else 0
                            
                            yoy_data.append({
                                "Year": year,
                                "Value": value,
                                "Absolute Change": change,
                                "Percentage Change": pct_change
                            })
                        
                        prev_value = row["Value"]
                    
                    if yoy_data:
                        yoy_df = pd.DataFrame(yoy_data)
                        
                        # Format the table
                        formatted_df = yoy_df.copy()
                        if is_percentage:
                            formatted_df["Value"] = formatted_df["Value"].map(lambda x: f"{x:.2f}%")
                            formatted_df["Absolute Change"] = formatted_df["Absolute Change"].map(lambda x: f"{x:.2f}%")
                        else:
                            formatted_df["Value"] = formatted_df["Value"].map(lambda x: f"${x:.2f}B")
                            formatted_df["Absolute Change"] = formatted_df["Absolute Change"].map(lambda x: f"${x:.2f}B")
                        
                        formatted_df["Percentage Change"] = formatted_df["Percentage Change"].map(lambda x: f"{x:.2f}%")
                        
                        st.dataframe(formatted_df, use_container_width=True)

if __name__ == "__main__":
    main() 