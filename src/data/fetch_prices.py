import yfinance as yf
import pandas as pd
import os

# NSE tickers need a .NS suffix for yfinance
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

OUTPUT_DIR = "data/raw/prices"

def fetch_price_history(name, ticker, years=5):
    print(f"Fetching {name} ({ticker})...")
    data = yf.download(ticker, period=f"{years}y", interval="1d", auto_adjust=True)

    if data.empty:
        print(f"  WARNING: no data returned for {ticker}")
        return

    data.to_csv(f"{OUTPUT_DIR}/{name}.csv")
    print(f"  saved {len(data)} rows")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for name, ticker in companies.items():
        fetch_price_history(name, ticker)

    print("\nDone. Check data/raw/prices/ for the CSV files.")
