import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
def clean(value):
    if pd.isna(value):
        return None
    return value

companies = [
    ("HDFCBANK", "HDFCBANK.NS", "Banking"),
    ("ICICIBANK", "ICICIBANK.NS", "Banking"),
    ("SBIN", "SBIN.NS", "Banking"),
    ("TCS", "TCS.NS", "IT"),
    ("INFY", "INFY.NS", "IT"),
    ("WIPRO", "WIPRO.NS", "IT"),
    ("RELIANCE", "RELIANCE.NS", "Energy"),
    ("ONGC", "ONGC.NS", "Energy"),
    ("HINDUNILVR", "HINDUNILVR.NS", "FMCG"),
    ("ITC", "ITC.NS", "FMCG"),
    ("TATAMOTORS", "TMPV.NS", "Auto"),
    ("MARUTI", "MARUTI.NS", "Auto"),
    ("SUNPHARMA", "SUNPHARMA.NS", "Pharma"),
    ("DRREDDY", "DRREDDY.NS", "Pharma"),
    ("ULTRACEMCO", "ULTRACEMCO.NS", "Cement"),
]

PRICES_DIR = "data/raw/prices"
FUNDAMENTALS_DIR = "data/raw/fundamentals"
VALUATION_FILE = "data/raw/valuation_snapshot.csv"


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def load_companies(cursor):
    print("Loading companies...")
    for name, ticker, sector in companies:
        cursor.execute(
            "INSERT IGNORE INTO companies (name, ticker, sector) VALUES (%s, %s, %s)",
            (name, ticker, sector),
        )
    print(f"  done ({len(companies)} companies)")


def get_company_id_map(cursor):
    cursor.execute("SELECT company_id, name FROM companies")
    return {name: company_id for company_id, name in cursor.fetchall()}


def load_stock_prices(cursor, company_id_map):
    print("Loading stock prices...")
    for name, ticker, sector in companies:
        company_id = company_id_map[name]
        filepath = f"{PRICES_DIR}/{name}.csv"

        df = pd.read_csv(filepath)
        rows = []
        for _, row in df.iterrows():
            rows.append((
                company_id,
                row["Date"],
                row.get("Open"),
                row.get("High"),
                row.get("Low"),
                row.get("Close"),
                row.get("Volume"),
            ))

        cursor.executemany(
            """INSERT IGNORE INTO stock_prices
               (company_id, price_date, open_price, high_price, low_price, close_price, volume)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            rows,
        )
        print(f"  {name}: {len(rows)} rows")


def load_financial_statements(cursor, company_id_map):
    print("Loading financial statements...")
    for name, ticker, sector in companies:
        company_id = company_id_map[name]
        filepath = f"{FUNDAMENTALS_DIR}/{name}.csv"

        df = pd.read_csv(filepath)
        rows = []
        for _, row in df.iterrows():
            # skip rows where the period date itself is missing
            if pd.isna(row.get("period_end_date")):
                continue
            rows.append((
                company_id,
                row["period_end_date"],
                clean(row.get("revenue")),
                clean(row.get("ebitda")),
                clean(row.get("ebit")),
                clean(row.get("net_income")),
                clean(row.get("total_debt")),
                clean(row.get("cash")),
                clean(row.get("equity")),
                clean(row.get("operating_cash_flow")),
                clean(row.get("free_cash_flow")),
            ))
        cursor.executemany(
            """INSERT IGNORE INTO financial_statements
               (company_id, period_end_date, revenue, ebitda, ebit, net_income,
                total_debt, cash, equity, operating_cash_flow, free_cash_flow)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            rows,
        )
        print(f"  {name}: {len(rows)} rows")


def load_valuation_metrics(cursor, company_id_map):
    print("Loading valuation metrics...")
    df = pd.read_csv(VALUATION_FILE)
    rows = []
    for _, row in df.iterrows():
        company_id = company_id_map[row["company"]]
        rows.append((
            company_id,
            clean(row.get("market_cap")),
            clean(row.get("pe_ratio")),
            clean(row.get("pb_ratio")),
            clean(row.get("dividend_yield")),
            clean(row.get("roe")),
            clean(row.get("shares_outstanding")),
        ))
    cursor.executemany(
        """INSERT IGNORE INTO valuation_metrics
           (company_id, market_cap, pe_ratio, pb_ratio, dividend_yield, roe, shares_outstanding)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        rows,
    )
    print(f"  done ({len(rows)} rows)")


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    load_companies(cursor)
    conn.commit()

    company_id_map = get_company_id_map(cursor)

    load_stock_prices(cursor, company_id_map)
    conn.commit()

    load_financial_statements(cursor, company_id_map)
    conn.commit()

    load_valuation_metrics(cursor, company_id_map)
    conn.commit()

    cursor.close()
    conn.close()
    print("\nAll data loaded into MySQL.")
