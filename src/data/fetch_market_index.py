import yfinance as yf
import os

OUTPUT_DIR = "data/raw/prices"
INDEX_TICKER = "^NSEI"  # Nifty 50


def fetch_index_history(years=5):
    print(f"Fetching Nifty 50 index ({INDEX_TICKER})...")
    data = yf.download(INDEX_TICKER, period=f"{years}y", interval="1d", auto_adjust=True)
    data.columns = data.columns.get_level_values(0)

    if data.empty:
        print("  WARNING: no data returned for Nifty 50")
        return

    data.reset_index(inplace=True)
    data.to_csv(f"{OUTPUT_DIR}/NIFTY50.csv", index=False)
    print(f"  saved {len(data)} rows")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fetch_index_history()
    print("\nDone. Check data/raw/prices/NIFTY50.csv")
