#!/usr/bin/env python3
"""
Metrics Interpreter for SEC filings data.

This module provides definitions and calculation methods for standard financial metrics
using data extracted from SEC filings. It serves as a central repository of financial
metrics formulas and calculation methods.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

# Comprehensive dictionary of financial metrics with calculation formulas
METRICS = {
    # --- Core Income Statement ---------------------------------------------------
    "revenue":                {"inputs": ["is.NetRevenue"],              "formula": "is.NetRevenue",                                           "desc": "Total top-line sales"},
    "cogs":                   {"inputs": ["is.CostOfRevenue"],           "formula": "is.CostOfRevenue",                                        "desc": "Cost of goods / services"},
    "gross_profit":           {"inputs": ["revenue","cogs"],             "formula": "revenue - cogs",                                          "desc": "Revenue minus COGS"},
    "rnd":                    {"inputs": ["is.RD"],                      "formula": "is.RD",                                                   "desc": "Research & development exp."},
    "sga":                    {"inputs": ["is.SG&A"],                    "formula": "is.SG&A",                                                 "desc": "Selling, general & admin"},
    "operating_income":       {"inputs": ["is.OperatingIncome"],         "formula": "is.OperatingIncome",                                      "desc": "EBIT; income from operations"},
    "ebit":                   {"inputs": ["operating_income"],           "formula": "operating_income",                                        "desc": "Synonym for operating income"},
    "interest_expense":       {"inputs": ["is.InterestExpense"],         "formula": "is.InterestExpense",                                      "desc": "Net interest cost"},
    "ebt":                    {"inputs": ["is.IncomeBeforeTax"],         "formula": "is.IncomeBeforeTax",                                      "desc": "Earnings before tax"},
    "tax_expense":            {"inputs": ["is.IncomeTax"],               "formula": "is.IncomeTax",                                           "desc": "Provision for income taxes"},
    "net_income":             {"inputs": ["is.NetIncome"],               "formula": "is.NetIncome",                                           "desc": "Bottom-line profit"},
    "eps_basic":              {"inputs": ["is.EPSBasic"],                "formula": "is.EPSBasic",                                            "desc": "Earnings per share, basic"},
    "eps_diluted":            {"inputs": ["is.EPSDiluted"],              "formula": "is.EPSDiluted",                                          "desc": "Earnings per share, diluted"},
    # --- Balance-Sheet Essentials ----------------------------------------------
    "cash":                   {"inputs": ["bs.CashAndEquivalents"],      "formula": "bs.CashAndEquivalents",                                   "desc": "Cash & cash equivalents"},
    "short_term_investments": {"inputs": ["bs.ShortTermInvestments"],    "formula": "bs.ShortTermInvestments",                                 "desc": "Marketable securities"},
    "accounts_receivable":    {"inputs": ["bs.AccountsReceivable"],      "formula": "bs.AccountsReceivable",                                   "desc": "Trade receivables"},
    "inventory":              {"inputs": ["bs.Inventory"],               "formula": "bs.Inventory",                                           "desc": "Inventories"},
    "current_assets":         {"inputs": ["bs.TotalCurrentAssets"],      "formula": "bs.TotalCurrentAssets",                                   "desc": "Total current assets"},
    "pp&e":                   {"inputs": ["bs.PP&E"],                    "formula": "bs.PP&E",                                                "desc": "Property, plant & equipment"},
    "goodwill":               {"inputs": ["bs.Goodwill"],                "formula": "bs.Goodwill",                                            "desc": "Goodwill intangible"},
    "total_assets":           {"inputs": ["bs.TotalAssets"],             "formula": "bs.TotalAssets",                                         "desc": "Sum of assets"},
    "accounts_payable":       {"inputs": ["bs.AccountsPayable"],         "formula": "bs.AccountsPayable",                                     "desc": "Trade accounts payable"},
    "deferred_revenue":       {"inputs": ["bs.DeferredRevenue"],         "formula": "bs.DeferredRevenue",                                     "desc": "Contract liabilities"},
    "current_liabilities":    {"inputs": ["bs.TotalCurrentLiabilities"], "formula": "bs.TotalCurrentLiabilities",                              "desc": "Due within 12 mo."},
    "long_term_debt":         {"inputs": ["bs.LongTermDebt"],            "formula": "bs.LongTermDebt",                                        "desc": "Borrowings >1 year"},
    "total_liabilities":      {"inputs": ["bs.TotalLiabilities"],        "formula": "bs.TotalLiabilities",                                    "desc": "All liabilities"},
    "shareholders_equity":    {"inputs": ["bs.TotalEquity"],             "formula": "bs.TotalEquity",                                         "desc": "Book value of equity"},
    # --- Cash Flow --------------------------------------------------------------
    "cfo":                    {"inputs": ["cf.CashFromOperations"],      "formula": "cf.CashFromOperations",                                   "desc": "Net cash from ops"},
    "capex":                  {"inputs": ["cf.CapEx"],                   "formula": "cf.CapEx",                                               "desc": "Capital expenditures"},
    "free_cash_flow":         {"inputs": ["cfo","capex"],                "formula": "cfo - capex",                                            "desc": "CFO minus capex"},
    "cff":                    {"inputs": ["cf.CashFromFinancing"],       "formula": "cf.CashFromFinancing",                                    "desc": "Cash from financing"},
    "cfi":                    {"inputs": ["cf.CashFromInvesting"],       "formula": "cf.CashFromInvesting",                                    "desc": "Cash from investing"},
    # --- Margins & Ratios -------------------------------------------------------
    "gross_margin_pct":       {"inputs": ["gross_profit","revenue"],     "formula": "gross_profit / revenue",                                 "desc": "Gross profit / revenue"},
    "operating_margin_pct":   {"inputs": ["operating_income","revenue"], "formula": "operating_income / revenue",                             "desc": "EBIT margin"},
    "net_margin_pct":         {"inputs": ["net_income","revenue"],       "formula": "net_income / revenue",                                   "desc": "Net profit margin"},
    "rd_pct":                 {"inputs": ["rnd","revenue"],              "formula": "rnd / revenue",                                          "desc": "R&D as % of sales"},
    "sga_pct":                {"inputs": ["sga","revenue"],              "formula": "sga / revenue",                                          "desc": "SG&A as % of sales"},
    "fcf_margin_pct":         {"inputs": ["free_cash_flow","revenue"],   "formula": "free_cash_flow / revenue",                               "desc": "FCF margin"},
    "ebitda":                 {"inputs": ["operating_income","is.D&A"],  "formula": "operating_income + is.D&A",                              "desc": "EBIT + depreciation & amort."},
    "ebitda_margin_pct":      {"inputs": ["ebitda","revenue"],           "formula": "ebitda / revenue",                                       "desc": "EBITDA margin"},
    "eps_growth_pct":         {"inputs": ["eps_diluted_t","eps_diluted_t-1"], "formula": "(eps_diluted_t/eps_diluted_t-1) - 1",               "desc": "YoY EPS growth"},
    "revenue_growth_pct":     {"inputs": ["revenue_t","revenue_t-1"],    "formula": "(revenue_t/revenue_t-1) - 1",                            "desc": "YoY top-line growth"},
    # --- Per-share & Market -----------------------------------------------------
    "shares_out":             {"inputs": ["is.WeightedAvgSharesDiluted"],"formula": "is.WeightedAvgSharesDiluted",                             "desc": "Diluted share count"},
    "market_cap":             {"inputs": ["price","shares_out"],         "formula": "price * shares_out",                                     "desc": "Price × diluted shares"},
    "enterprise_value":       {"inputs": ["market_cap","total_liabilities","cash"], "formula": "market_cap + total_liabilities - cash",        "desc": "EV = Mcap + debt - cash"},
    "ev_ebitda":              {"inputs": ["enterprise_value","ebitda"],  "formula": "enterprise_value / ebitda",                              "desc": "EV / EBITDA multiple"},
    "price_sales":            {"inputs": ["market_cap","revenue"],       "formula": "market_cap / revenue",                                   "desc": "P/S ratio"},
    "price_earnings":         {"inputs": ["price","eps_diluted"],        "formula": "price / eps_diluted",                                    "desc": "Trailing P/E"},
    "dividend_yield_pct":     {"inputs": ["dividend_per_share","price"], "formula": "dividend_per_share / price",                             "desc": "Dividends / price"},
    # --- Return Metrics ---------------------------------------------------------
    "roic_pct":               {"inputs": ["nopat","invested_capital"],   "formula": "nopat / invested_capital",                               "desc": "Return on invested capital"},
    "roe_pct":                {"inputs": ["net_income","shareholders_equity"], "formula": "net_income / shareholders_equity",                "desc": "Return on equity"},
    "roa_pct":                {"inputs": ["net_income","total_assets"],  "formula": "net_income / total_assets",                              "desc": "Return on assets"},
    # --- Leverage & Liquidity ---------------------------------------------------
    "current_ratio":          {"inputs": ["current_assets","current_liabilities"], "formula": "current_assets / current_liabilities",         "desc": "Liquidity ratio"},
    "quick_ratio":            {"inputs": ["cash","short_term_investments","accounts_receivable","current_liabilities"],                       "formula": "(cash + short_term_investments + accounts_receivable) / current_liabilities", "desc": "Acid-test ratio"},
    "debt_equity":            {"inputs": ["long_term_debt","shareholders_equity"], "formula": "long_term_debt / shareholders_equity",         "desc": "Leverage ratio"},
    "debt_ebitda":            {"inputs": ["long_term_debt","ebitda"],    "formula": "long_term_debt / ebitda",                                "desc": "Debt / EBITDA"},
    "interest_coverage":      {"inputs": ["ebit","interest_expense"],    "formula": "ebit / abs(interest_expense)",                           "desc": "EBIT / Interest"},
    # --- Cash Efficiency --------------------------------------------------------
    "ocf_conversion_pct":     {"inputs": ["cfo","net_income"],           "formula": "cfo / net_income",                                       "desc": "Cash conversion (ops)"},
    "capex_sales_pct":        {"inputs": ["capex","revenue"],            "formula": "capex / revenue",                                        "desc": "Capex intensity"},
    "dividend_payout_pct":    {"inputs": ["dividend_per_share","eps_diluted"], "formula": "dividend_per_share / eps_diluted",                "desc": "Payout ratio"},
    # --- Valuation Extras -------------------------------------------------------
    "ev_sales":               {"inputs": ["enterprise_value","revenue"], "formula": "enterprise_value / revenue",                             "desc": "EV / Sales"},
    "ev_ebit":                {"inputs": ["enterprise_value","ebit"],    "formula": "enterprise_value / ebit",                                "desc": "EV / EBIT"},
    "fcf_yield_pct":          {"inputs": ["free_cash_flow","market_cap"], "formula": "free_cash_flow / market_cap",                            "desc": "FCF / market cap"},
    # --- Growth Tailwinds -------------------------------------------------------
    "rd_growth_pct":          {"inputs": ["rnd_t","rnd_t-1"],            "formula": "(rnd_t/rnd_t-1) - 1",                                    "desc": "YoY R&D growth"},
    "capex_growth_pct":       {"inputs": ["capex_t","capex_t-1"],        "formula": "(capex_t/capex_t-1) - 1",                                "desc": "YoY CapEx growth"},
    "employees":              {"inputs": ["10K.Employees"],             "formula": "10K.Employees",                                          "desc": "Full-time headcount"},
    "revenue_per_employee":   {"inputs": ["revenue","employees"],        "formula": "revenue / employees",                                    "desc": "Efficiency metric"},
    # --- Segment / Geo (generic placeholders) ----------------------------------
    "segment_revenue":        {"inputs": ["segment_df"],                 "formula": "lookup(segment_df, 'SegmentName')",                      "desc": "Revenue for a specific segment"},
    "geo_revenue":            {"inputs": ["geo_df"],                     "formula": "lookup(geo_df, 'Region')",                               "desc": "Revenue for a specific region"},
    # --- Market Performance -----------------------------------------------------
    "total_return_1y_pct":    {"inputs": ["price_t","price_t-252"],      "formula": "(price_t/price_t-252) - 1",                               "desc": "1-year price return"},
    "beta_2y":                {"inputs": ["daily_returns","index_returns"], "formula": "regression_beta(daily_returns, index_returns)",      "desc": "2-year beta vs S&P 500"},
    "volatility_30d":         {"inputs": ["daily_returns_30d"],          "formula": "std(daily_returns_30d) * sqrt(252)",                     "desc": "30-day annualized vol"},
    # --- ESG / Other ------------------------------------------------------------
    "carbon_intensity":       {"inputs": ["ghg_scope1","revenue"],       "formula": "ghg_scope1 / revenue",                                   "desc": "tCO₂e / $ revenue"},
    "board_independence_pct": {"inputs": ["board_independent","board_total"], "formula": "board_independent / board_total",                  "desc": "Governance metric"},
    # --- Defensive Dupes (makes 100 lines) -------------------------------------
    "preferred_dividends":    {"inputs": ["is.PreferredDividends"],      "formula": "is.PreferredDividends",                                  "desc": "Preferred payouts"},
    "tangible_book_value":    {"inputs": ["shareholders_equity","goodwill"], "formula": "shareholders_equity - goodwill",                     "desc": "Equity less intangibles"},
    "price_book":             {"inputs": ["price","tangible_book_value_per_share"], "formula": "price / tangible_book_value_per_share",      "desc": "P/B on tangible BV"},
    "working_capital":        {"inputs": ["current_assets","current_liabilities"], "formula": "current_assets - current_liabilities",        "desc": "Operational liquidity"},
    "days_sales_outstanding": {"inputs": ["accounts_receivable","revenue"], "formula": "(accounts_receivable / revenue) * 365",              "desc": "Receivables / sales days"},
    "days_inventory":         {"inputs": ["inventory","cogs"],           "formula": "(inventory / cogs) * 365",                               "desc": "Inventory days"},
    "days_payables":          {"inputs": ["accounts_payable","cogs"],    "formula": "(accounts_payable / cogs) * 365",                        "desc": "Payables days"},
    "cash_conversion_cycle":  {"inputs": ["days_inventory","days_sales_outstanding","days_payables"], "formula": "days_inventory + days_sales_outstanding - days_payables", "desc": "Supply-chain cash cycle"},
    "interest_bearing_debt":  {"inputs": ["long_term_debt","bs.ShortTermDebt"], "formula": "long_term_debt + bs.ShortTermDebt",             "desc": "All debt obligations"},
    "ltm_revenue":            {"inputs": ["revenue_t","revenue_t-1","revenue_t-2","revenue_t-3"], "formula": "sum(last_4_quarters)",         "desc": "Trailing-12-month revenue"}
}

# Define metric aliases (alternative names for the same metric)
METRIC_ALIASES = {
    "sales": "revenue",
    "top_line": "revenue",
    "profits": "net_income",
    "earnings": "net_income",
    "bottom_line": "net_income",
    "r&d": "rnd",
    "research_and_development": "rnd",
    "operating_profit": "operating_income",
    "ebit_margin": "operating_margin_pct",
    "profit_margin": "net_margin_pct",
    "net_profit_margin": "net_margin_pct",
    "gross_margin": "gross_margin_pct",
    "fcf": "free_cash_flow",
    "operating_cash_flow": "cfo",
    "ppe": "pp&e",
    "property_plant_equipment": "pp&e",
    "debt": "long_term_debt",
    "equity": "shareholders_equity",
    "book_value": "shareholders_equity",
    "assets": "total_assets",
    "liabilities": "total_liabilities",
    "ar": "accounts_receivable",
    "ap": "accounts_payable",
    "pe_ratio": "price_earnings",
    "pe": "price_earnings",
    "ps": "price_sales",
    "ps_ratio": "price_sales",
}

class MetricsInterpreter:
    """
    Interpreter for financial metrics calculation and comparison.
    
    This class provides methods to:
    1. Identify which metrics are being requested in natural language
    2. Map the metrics to calculation formulas
    3. Calculate the metrics based on available data
    4. Generate explanations for metric calculations
    """
    
    def __init__(self):
        """Initialize the metrics interpreter."""
        logger.info("MetricsInterpreter initialized")
    
    def identify_metrics(self, query: str) -> List[str]:
        """
        Identify which metrics are being asked about in a query.
        
        Args:
            query: The natural language query
            
        Returns:
            List of identified metric names
        """
        query = query.lower()
        metrics = []
        
        # Prepare a cleaned version of the query for matching
        # Replace common punctuation with spaces
        clean_query = re.sub(r'[.,;:?!]', ' ', query)
        # Replace apostrophes with empty string
        clean_query = re.sub(r"['']", '', clean_query)
        
        # Check for direct mentions of metrics in the query
        for metric_name in METRICS:
            # Replace underscores with spaces for matching
            normalized_name = metric_name.replace('_', ' ')
            if normalized_name in clean_query:
                metrics.append(metric_name)
                continue
                
            # Check for metric with "pct" or "percentage" suffix
            if metric_name.endswith('_pct'):
                base_name = metric_name[:-4].replace('_', ' ')
                if (base_name in clean_query and 
                    ('percentage' in clean_query or 'percent' in clean_query or '%' in clean_query)):
                    metrics.append(metric_name)
                    continue
        
        # Check for metric aliases
        for alias, metric_name in METRIC_ALIASES.items():
            normalized_alias = alias.replace('_', ' ')
            if normalized_alias in clean_query and metric_name not in metrics:
                metrics.append(metric_name)
        
        return metrics
    
    def calculate_metric(self, metric_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a specific metric based on available data.
        
        Args:
            metric_name: Name of the metric to calculate
            data: Dictionary of available financial data
            
        Returns:
            Dictionary with calculation result and metadata
        """
        # Resolve alias if needed
        if metric_name in METRIC_ALIASES:
            metric_name = METRIC_ALIASES[metric_name]
            
        # Check if metric exists in our definitions
        if metric_name not in METRICS:
            return {
                "success": False,
                "error": f"Unknown metric '{metric_name}'"
            }
            
        metric_spec = METRICS[metric_name]
        inputs = metric_spec["inputs"]
        formula = metric_spec["formula"]
        
        # Check if we have all required inputs
        missing_inputs = [inp for inp in inputs if inp not in data]
        if missing_inputs:
            return {
                "success": False,
                "error": f"Missing data for inputs: {', '.join(missing_inputs)}",
                "metric": metric_name,
                "missing_inputs": missing_inputs
            }
            
        try:
            # Use the safer calc function to calculate the metric
            result = calc(METRICS, metric_name, data)
            
            # For percentage metrics, convert to percentage value
            if metric_name.endswith('_pct') and not isinstance(result, str):
                result = result * 100
            
            return {
                "success": True,
                "metric": metric_name,
                "value": result,
                "formula": formula,
                "description": metric_spec["desc"],
                "inputs_used": {inp: data[inp] for inp in inputs if inp in data}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating metric: {str(e)}",
                "metric": metric_name,
                "formula": formula
            }
    
    def interpret_metric_request(self, query: str, ticker: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Interpret and fulfill a natural language request for financial metrics.
        
        Args:
            query: The natural language query
            ticker: Company ticker
            data: Optional pre-loaded financial data
            
        Returns:
            Dictionary with interpretation results
        """
        logger.info(f"Interpreting metric request: '{query}' for {ticker}")
        
        # Identify requested metrics
        requested_metrics = self.identify_metrics(query)
        
        if not requested_metrics:
            # If no specific metrics were identified, this might be a general question
            return {
                "success": False,
                "error": "Could not identify specific metrics in the query",
                "query": query,
                "ticker": ticker,
                "requires_llm": True  # Flag that this needs LLM-based interpretation
            }
            
        # If data was provided, calculate the metrics
        results = {}
        if data:
            for metric in requested_metrics:
                results[metric] = self.calculate_metric(metric, data)
                
            return {
                "success": any(r.get("success", False) for r in results.values()),
                "query": query,
                "ticker": ticker,
                "metrics": requested_metrics,
                "results": results
            }
        else:
            # Just return the identified metrics if no data is provided
            return {
                "success": True,
                "query": query,
                "ticker": ticker,
                "metrics": requested_metrics
            }

    def get_metric_definition(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the definition and calculation formula for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Dictionary with metric definition
        """
        # Resolve alias if needed
        if metric_name in METRIC_ALIASES:
            canonical_name = METRIC_ALIASES[metric_name]
            original_name = metric_name
            metric_name = canonical_name
        else:
            original_name = None
            
        # Check if metric exists
        if metric_name not in METRICS:
            return {
                "success": False,
                "error": f"Unknown metric '{metric_name}'"
            }
            
        metric_spec = METRICS[metric_name]
        
        return {
            "success": True,
            "metric": metric_name,
            "original_name": original_name,
            "description": metric_spec["desc"],
            "formula": metric_spec["formula"],
            "inputs": metric_spec["inputs"],
            "is_alias": original_name is not None
        }


def calc(metrics_dict, key, data):
    """
    Calculate a metric based on the metrics dictionary and available data.
    
    This function safely evaluates financial metric formulas. It handles:
    1. Simple direct references to financial statement items
    2. Complex formulas with multiple inputs and operations
    3. Safe variable name transformation for special characters like '.', '&', and '-'
    4. Error handling for missing inputs
    
    Args:
        metrics_dict: Dictionary of metric definitions
        key: Metric key to calculate
        data: Dictionary of available financial data
        
    Returns:
        Calculated metric value
    
    Raises:
        ValueError: If inputs are missing or formula evaluation fails
    """
    spec = metrics_dict[key]
    
    # For direct references to financial statement items, evaluate directly
    if len(spec["inputs"]) == 1 and spec["formula"] == spec["inputs"][0]:
        if spec["inputs"][0] in data:
            return data[spec["inputs"][0]]
        else:
            raise ValueError(f"Missing value for input: {spec['inputs'][0]}")
    
    # Prepare input values
    input_values = {}
    for inp in spec["inputs"]:
        if inp not in data:
            raise ValueError(f"Missing values for inputs: {[inp for inp in spec['inputs'] if inp not in data]}")
        
        # Make a safe variable name from the input
        safe_name = inp.replace('.', '_').replace('&', 'and').replace('-', '_')
        input_values[safe_name] = data[inp]
    
    # Create a safe formula by replacing problematic characters in variable names
    safe_formula = spec["formula"]
    for inp in spec["inputs"]:
        safe_name = inp.replace('.', '_').replace('&', 'and').replace('-', '_')
        if inp != safe_name:
            safe_formula = safe_formula.replace(inp, safe_name)
    
    # Create a safe environment for formula evaluation
    safe_globals = {"__builtins__": None}
    safe_locals = {**input_values, 'abs': abs, 'max': max, 'min': min}
    
    # Evaluate the formula safely
    try:
        result = eval(safe_formula, safe_globals, safe_locals)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating formula '{safe_formula}': {str(e)}")


# Function to get a list of all available metrics
def get_available_metrics() -> List[Dict[str, Any]]:
    """
    Get a list of all available metrics with their descriptions.
    
    Returns:
        List of dictionaries with metric information
    """
    return [
        {
            "name": name,
            "description": info["desc"],
            "formula": info["formula"],
            "inputs": info["inputs"]
        }
        for name, info in METRICS.items()
    ]


# Function to find metrics based on keywords
def find_metrics_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """
    Find metrics that match a keyword in their name or description.
    
    Args:
        keyword: Keyword to search for
        
    Returns:
        List of matching metrics
    """
    keyword = keyword.lower()
    matches = []
    
    for name, info in METRICS.items():
        if (keyword in name.lower() or 
            keyword in info["desc"].lower() or
            any(keyword in input_name.lower() for input_name in info["inputs"])):
            
            matches.append({
                "name": name,
                "description": info["desc"],
                "formula": info["formula"],
                "inputs": info["inputs"]
            })
            
    return matches
