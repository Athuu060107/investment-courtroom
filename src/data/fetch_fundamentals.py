import yfinance as yf
import pandas as pd
import os

companies = {
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "WIPRO": "WIPRO.NS",
    "RELIANCE": "RELIANCE.NS",
    "ONGC": "ONGC.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "TATAMOTORS": "TMPV.NS",
    "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "DRREDDY": "DRREDDY.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
}

STATEMENTS_DIR = "data/raw/fundamentals"
VALUATION_FILE = "data/raw/valuation_snapshot.csv"


def get_row_safe(df, row_name):
    # financial statement rows aren't always present for every company
    if df is None or df.empty or row_name not in df.index:
        return None
    return df.loc[row_name]


def fetch_financial_statements(name, ticker):
    stock = yf.Ticker(ticker)

    income = stock.financials       # annual income statement
    balance = stock.balance_sheet    # annual balance sheet
    cashflow = stock.cashflow        # annual cash flow statement

    revenue = get_row_safe(income, "Total Revenue")
    ebitda = get_row_safe(income, "EBITDA")
    ebit = get_row_safe(income, "EBIT")
    net_income = get_row_safe(income, "Net Income")

    total_debt = get_row_safe(balance, "Total Debt")
    cash = get_row_safe(balance, "Cash And Cash Equivalents")
    equity = get_row_safe(balance, "Stockholders Equity")

    op_cash_flow = get_row_safe(cashflow, "Operating Cash Flow")
    free_cash_flow = get_row_safe(cashflow, "Free Cash Flow")

    rows = {
        "revenue": revenue,
        "ebitda": ebitda,
        "ebit": ebit,
        "net_income": net_income,
        "total_debt": total_debt,
        "cash": cash,
        "equity": equity,
        "operating_cash_flow": op_cash_flow,
        "free_cash_flow": free_cash_flow,
    }

    # warn about anything missing
    for field, series in rows.items():
        if series is None:
            print(f"  WARNING: {field} not available for {name}")

    df = pd.DataFrame(rows)
    df.index.name = "period_end_date"
    return df


def fetch_valuation_snapshot(name, ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    snapshot = {
        "company": name,
        "ticker": ticker,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "roe": info.get("returnOnEquity"),
        "shares_outstanding": info.get("sharesOutstanding"),
    }

    for field, value in snapshot.items():
        if value is None and field not in ("company", "ticker"):
            print(f"  WARNING: {field} not available for {name}")

    return snapshot


if __name__ == "__main__":
    os.makedirs(STATEMENTS_DIR, exist_ok=True)
    valuation_rows = []

    for name, ticker in companies.items():
        print(f"Fetching fundamentals for {name} ({ticker})...")

        statements = fetch_financial_statements(name, ticker)
        statements.to_csv(f"{STATEMENTS_DIR}/{name}.csv")

        snapshot = fetch_valuation_snapshot(name, ticker)
        valuation_rows.append(snapshot)

    valuation_df = pd.DataFrame(valuation_rows)
    valuation_df.to_csv(VALUATION_FILE, index=False)

    print(f"\nDone. Financial statements saved in {STATEMENTS_DIR}/")
    print(f"Valuation snapshot saved to {VALUATION_FILE}")
