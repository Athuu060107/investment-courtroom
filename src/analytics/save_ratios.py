import mysql.connector
import os
from datetime import date
import math
from dotenv import load_dotenv

from src.analytics.price_metrics import get_all_metrics, calculate_beta
from src.analytics.fundamental_ratios import calculate_ratios

load_dotenv()

companies = [
    "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "WIPRO",
    "RELIANCE", "ONGC", "HINDUNILVR", "ITC", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "DRREDDY", "ULTRACEMCO",
]


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="config/ca.pem",
    )

def get_company_id(cursor, name):
    cursor.execute("SELECT company_id FROM companies WHERE name = %s", (name,))
    row = cursor.fetchone()
    return row[0] if row else None


def build_ratio_row(name):
    price_metrics = get_all_metrics(name)
    beta = calculate_beta(name)
    fundamentals = calculate_ratios(name)

    if price_metrics is None or fundamentals is None or fundamentals.empty:
        print(f"  skipping {name}, missing data")
        return None

    # use the most recent year's fundamentals
    latest = fundamentals.iloc[-1]

    return {
        "cagr": price_metrics["cagr"],
        "volatility": price_metrics["volatility"],
        "max_drawdown": price_metrics["max_drawdown"],
        "sharpe_ratio": price_metrics["sharpe_ratio"],
        "beta": round(beta, 2),
        "roe": latest["roe"] if not pd_isna(latest["roe"]) else None,
        "roce": latest["roce"] if not pd_isna(latest["roce"]) else None,
        "net_margin": latest["net_margin"] if not pd_isna(latest["net_margin"]) else None,
        "operating_margin": latest["operating_margin"] if not pd_isna(latest["operating_margin"]) else None,
    }


def pd_isna(value):
    import pandas as pd
    return pd.isna(value)
def clean(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    for name in companies:
        print(f"Calculating ratios for {name}...")
        company_id = get_company_id(cursor, name)
        row = build_ratio_row(name)

        if row is None or company_id is None:
            continue

        cursor.execute(
            """
            INSERT INTO financial_ratios
                (company_id, cagr, volatility, max_drawdown, sharpe_ratio, beta,
                 roe, roce, net_margin, operating_margin, calculated_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cagr = VALUES(cagr),
                volatility = VALUES(volatility),
                max_drawdown = VALUES(max_drawdown),
                sharpe_ratio = VALUES(sharpe_ratio),
                beta = VALUES(beta),
                roe = VALUES(roe),
                roce = VALUES(roce),
                net_margin = VALUES(net_margin),
                operating_margin = VALUES(operating_margin),
                calculated_on = VALUES(calculated_on)
            """,
            (
                company_id,
                clean(row["cagr"]), clean(row["volatility"]), clean(row["max_drawdown"]),
                clean(row["sharpe_ratio"]), clean(row["beta"]),
                clean(row["roe"]), clean(row["roce"]), clean(row["net_margin"]), clean(row["operating_margin"]),
                date.today(),
            ),
        )
        print(f"  done")

    conn.commit()
    cursor.close()
    conn.close()
    print("\nAll ratios calculated and saved to financial_ratios table.")
