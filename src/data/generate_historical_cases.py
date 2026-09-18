import mysql.connector
import os
import numpy as np
from datetime import timedelta
from dotenv import load_dotenv

from src.analytics.price_metrics import get_price_history

load_dotenv()

companies = [
    "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "WIPRO",
    "RELIANCE", "ONGC", "HINDUNILVR", "ITC", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "DRREDDY", "ULTRACEMCO",
]


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_company_id(cursor, name):
    cursor.execute("SELECT company_id FROM companies WHERE name = %s", (name,))
    row = cursor.fetchone()
    return row[0] if row else None


def build_case(company_name):
    price_df = get_price_history(company_name)
    if price_df.empty:
        return None

    latest_date = price_df["price_date"].max()
    case_date_target = latest_date - timedelta(days=730)  # roughly 2 years back

    # find the closest actual trading day to our target date
    price_df["diff"] = (price_df["price_date"] - case_date_target).abs()
    case_row = price_df.loc[price_df["diff"].idxmin()]
    case_date = case_row["price_date"]
    price_at_case = case_row["close_price"]

    latest_price = price_df[price_df["price_date"] == latest_date]["close_price"].values[0]

    # find the price roughly 1 year after the case date, for a real forward return
    one_year_later_target = case_date + timedelta(days=365)
    price_df["diff_1y"] = (price_df["price_date"] - one_year_later_target).abs()
    one_year_row = price_df.loc[price_df["diff_1y"].idxmin()]
    price_1y_later = one_year_row["close_price"]

    outcome_return_1y = round(((price_1y_later - price_at_case) / price_at_case) * 100, 2)
    outcome_return_to_date = round(((latest_price - price_at_case) / price_at_case) * 100, 2)

    # metrics as they would have looked using only data up to the case date
    history_up_to_case = price_df[price_df["price_date"] <= case_date]
    if len(history_up_to_case) < 30:
        return None

    daily_returns = history_up_to_case["close_price"].pct_change().dropna()
    volatility_as_of_case = round(daily_returns.std() * np.sqrt(252) * 100, 2)

    years = (case_date - history_up_to_case["price_date"].min()).days / 365.25
    if years > 0:
        cagr_as_of_case = round(
            ((price_at_case / history_up_to_case["close_price"].iloc[0]) ** (1 / years) - 1) * 100, 2
        )
    else:
        cagr_as_of_case = None

    return {
        "case_date": case_date,
        "price_at_case": round(price_at_case, 2),
        "latest_price": round(latest_price, 2),
        "outcome_return_1y": outcome_return_1y,
        "outcome_return_to_date": outcome_return_to_date,
        "cagr_as_of_case": cagr_as_of_case,
        "volatility_as_of_case": volatility_as_of_case,
    }


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    for name in companies:
        print(f"Building case for {name}...")
        company_id = get_company_id(cursor, name)
        case = build_case(name)

        if case is None or company_id is None:
            print(f"  skipping {name}, not enough data")
            continue

        cursor.execute(
            """
            INSERT INTO investment_cases
                (company_id, case_date, price_at_case, latest_price, outcome_return_1y,
                 outcome_return_to_date, cagr_as_of_case, volatility_as_of_case)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                case_date = VALUES(case_date),
                price_at_case = VALUES(price_at_case),
                latest_price = VALUES(latest_price),
                outcome_return_1y = VALUES(outcome_return_1y),
                outcome_return_to_date = VALUES(outcome_return_to_date),
                cagr_as_of_case = VALUES(cagr_as_of_case),
                volatility_as_of_case = VALUES(volatility_as_of_case)
            """,
            (
                company_id, case["case_date"], case["price_at_case"], case["latest_price"],
                case["outcome_return_1y"], case["outcome_return_to_date"],
                case["cagr_as_of_case"], case["volatility_as_of_case"],
            ),
        )
        print(f"  case date: {case['case_date']}, 1yr return: {case['outcome_return_1y']}%")

    conn.commit()
    cursor.close()
    conn.close()
    print("\nAll historical cases generated.")
