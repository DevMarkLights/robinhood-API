from flask import Blueprint, jsonify
import yfinance as yf
import numpy as np
import time
import pandas as pd
from cachetools import TTLCache

financialStatement = Blueprint('financialStatement', __name__)
# cache = TTLCache(maxsize=100, ttl=300)

ROWS_OF_INTEREST = [
        "Total Revenue",
        "Cost Of Revenue",
        "Gross Profit",
        "Operating Income",
        "Interest Expense",
        "Pretax Income",
        "Tax Provision",
        "Net Income",
    ]

@financialStatement.get('/ticker/financialStatement/<ticker>')
def getFinancialStatement(ticker: str):
    # if ticker in cache:
    #     return cache[ticker]
    
    stock = yf.Ticker(ticker)
    
    q_income = stock.quarterly_income_stmt
    a_income = stock.income_stmt
 
    if q_income.empty and a_income.empty:
        return jsonify({"error": f"No financial data found for ticker '{ticker}'"}), 404

    statements = {
        "income_statement_annual": df_to_json(a_income),
        "income_statement_quarterly": df_to_json(q_income),
        "balance_sheet_annual": df_to_json(stock.balance_sheet),
        "balance_sheet_quarterly": df_to_json(stock.quarterly_balance_sheet),
        "cash_flow_annual": df_to_json(stock.cashflow),
        "cash_flow_quarterly": df_to_json(stock.quarterly_cashflow),
    }

    response = {
        "ticker": ticker.upper(),
        "summary": build_yoy_summary(q_income, a_income),
        "statements": statements,
    }

    # cache[ticker] = jsonify(response)
 
    return jsonify(response)
    return data

def print_summary(data: dict):
    q_income = data["income_statement_quarterly"]
 
    if q_income.empty:
        print("No quarterly income statement data returned.")
        return
 
    latest_col = q_income.columns[0]
    print(f"\n=== TMUS Latest Quarter: {latest_col.date()} ===\n")
 
    rows_of_interest = [
        "Total Revenue",
        "Cost Of Revenue",
        "Gross Profit",
        "Operating Income",
        "Interest Expense",
        "Pretax Income",
        "Tax Provision",
        "Net Income",
    ]

    yoy_col = q_income.columns[4] if len(q_income.columns) > 4 else None
    if yoy_col is not None:
        print(f"(YoY compares against quarter ending {yoy_col.date()})\n")
    else:
        print("(Not enough quarterly history for a true YoY comparison -- "
              "yfinance free tier typically only returns ~4-5 quarters.\n"
              "Falling back to annual data for YoY below.)\n")
    

    print(f"{'Metric':<20}{'Latest Q':>14}{'YoY Q':>14}{'YoY %':>10}")
    for row in rows_of_interest:
        if row not in q_income.index:
            continue
        latest_val = q_income.loc[row, latest_col]
        if yoy_col is not None:
            prior_val = q_income.loc[row, yoy_col]
            pct = (latest_val - prior_val) / abs(prior_val) * 100 if prior_val else float("nan")
            print(f"{row:<20}{latest_val / 1e9:>13,.2f}B{prior_val / 1e9:>13,.2f}B{pct:>9,.1f}%")
        else:
            print(f"{row:<20}{latest_val / 1e9:>13,.2f}B{'n/a':>14}{'n/a':>10}")
 
    # Annual fallback / supplement -- always show this since it gives a clean
    # true YoY (fiscal year over fiscal year).
    a_income = data["income_statement_annual"]
    if not a_income.empty and len(a_income.columns) >= 2:
        latest_a, prior_a = a_income.columns[0], a_income.columns[1]
        print(f"\n=== Annual YoY: FY{latest_a.year} vs FY{prior_a.year} ===\n")
        print(f"{'Metric':<20}{'FY' + str(latest_a.year):>14}{'FY' + str(prior_a.year):>14}{'YoY %':>10}")
        for row in rows_of_interest:
            if row not in a_income.index:
                continue
            latest_val = a_income.loc[row, latest_a]
            prior_val = a_income.loc[row, prior_a]
            pct = (latest_val - prior_val) / abs(prior_val) * 100 if prior_val else float("nan")
            print(f"{row:<20}{latest_val / 1e9:>13,.2f}B{prior_val / 1e9:>13,.2f}B{pct:>9,.1f}%")
 
def df_to_json(df: pd.DataFrame) -> dict:
    """Convert a yfinance DataFrame (rows=line items, cols=period dates) into
    a JSON-safe dict: {row_label: {period_iso_date: value_or_None}}.
    Handles NaN/NaT/np types that jsonify can't serialize on its own.
    """
    if df is None or df.empty:
        return {}
 
    out = {}
    for row_label in df.index:
        row_data = {}
        for col in df.columns:
            val = df.loc[row_label, col]
            period_key = col.date().isoformat() if hasattr(col, "date") else str(col)
 
            if pd.isna(val):
                row_data[period_key] = None
            elif isinstance(val, (np.integer,)):
                row_data[period_key] = int(val)
            elif isinstance(val, (np.floating,)):
                row_data[period_key] = float(val)
            else:
                row_data[period_key] = val
        out[str(row_label)] = row_data
    return out


def build_yoy_summary(q_income: pd.DataFrame, a_income: pd.DataFrame) -> dict:
    """Builds quarterly YoY (if enough history) and annual YoY summaries."""
    summary = {"quarterly_yoy": None, "annual_yoy": None}
 
    if q_income is not None and not q_income.empty:
        latest_col = q_income.columns[0]
        yoy_col = q_income.columns[4] if len(q_income.columns) > 4 else None
 
        quarterly = {
            "latest_period": latest_col.date().isoformat(),
            "comparison_period": yoy_col.date().isoformat() if yoy_col is not None else None,
            "metrics": {},
        }
 
        for row in ROWS_OF_INTEREST:
            if row not in q_income.index:
                continue
            latest_val = q_income.loc[row, latest_col]
            latest_val = None if pd.isna(latest_val) else float(latest_val)
 
            if yoy_col is not None:
                prior_val = q_income.loc[row, yoy_col]
                prior_val = None if pd.isna(prior_val) else float(prior_val)
                pct = None
                if latest_val is not None and prior_val:
                    pct = round((latest_val - prior_val) / abs(prior_val) * 100, 2)
                quarterly["metrics"][row] = {
                    "latest": latest_val,
                    "prior_year": prior_val,
                    "yoy_pct": pct,
                }
            else:
                quarterly["metrics"][row] = {
                    "latest": latest_val,
                    "prior_year": None,
                    "yoy_pct": None,
                }
        summary["quarterly_yoy"] = quarterly
 
    if a_income is not None and not a_income.empty and len(a_income.columns) >= 2:
        latest_a, prior_a = a_income.columns[0], a_income.columns[1]
        annual = {
            "latest_fy": latest_a.year,
            "prior_fy": prior_a.year,
            "metrics": {},
        }
 
        for row in ROWS_OF_INTEREST:
            if row not in a_income.index:
                continue
            latest_val = a_income.loc[row, latest_a]
            prior_val = a_income.loc[row, prior_a]
            latest_val = None if pd.isna(latest_val) else float(latest_val)
            prior_val = None if pd.isna(prior_val) else float(prior_val)
            pct = None
            if latest_val is not None and prior_val:
                pct = round((latest_val - prior_val) / abs(prior_val) * 100, 2)
            annual["metrics"][row] = {
                "latest": latest_val,
                "prior_year": prior_val,
                "yoy_pct": pct,
            }
        summary["annual_yoy"] = annual
 
    return summary

def export_to_csv(data: dict, prefix: str = "tmus"):
    for name, df in data.items():
        if not df.empty:
            filename = f"{prefix}_{name}.csv"
            df.to_csv(filename)
            print(f"Saved {filename}")
 
 
if __name__ == "__main__":
    financials = getFinancialStatement("TMUS")
    print_summary(financials)
    # export_to_csv(financials)