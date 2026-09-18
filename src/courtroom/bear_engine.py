import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="config/ca.pem",
    )

def get_company_data(company_name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT fr.*, vm.pe_ratio, vm.pb_ratio
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        LEFT JOIN valuation_metrics vm ON vm.company_id = c.company_id
        WHERE c.name = %s
        """,
        (company_name,),
    )
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data


def get_latest_debt_equity(company_name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT fs.total_debt, fs.equity
        FROM financial_statements fs
        JOIN companies c ON fs.company_id = c.company_id
        WHERE c.name = %s
        ORDER BY fs.period_end_date DESC
        LIMIT 1
        """,
        (company_name,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None or row["total_debt"] is None or row["equity"] is None or row["equity"] == 0:
        return None

    return row["total_debt"] / row["equity"]


def build_bear_case(company_name):
    data = get_company_data(company_name)
    if data is None:
        return []

    arguments = []

    if data["cagr"] is not None and data["cagr"] < 0:
        arguments.append(f"Value has declined: the stock has lost {abs(data['cagr'])}% per year on average over the last 5 years.")

    if data["volatility"] is not None and data["volatility"] > 30:
        arguments.append(f"High volatility: an annualized volatility of {data['volatility']}% means large, unpredictable price swings.")

    if data["max_drawdown"] is not None and data["max_drawdown"] < -40:
        arguments.append(f"Severe drawdown risk: the stock has fallen as much as {data['max_drawdown']}% from a previous peak.")

    if data["sharpe_ratio"] is not None and data["sharpe_ratio"] < 0:
        arguments.append(f"Poor risk-adjusted return: a negative Sharpe ratio of {data['sharpe_ratio']} means the risk taken wasn't rewarded.")

    if data["beta"] is not None and data["beta"] > 1.2:
        arguments.append(f"Amplifies market swings: a beta of {data['beta']} means the stock moves more sharply than the Nifty 50, in both directions.")

    if data["pe_ratio"] is not None and data["pe_ratio"] > 40:
        arguments.append(f"Expensive valuation: a P/E ratio of {data['pe_ratio']} implies the market is pricing in a lot of future growth already.")

    if data["roce"] is None:
        arguments.append("Limited capital-efficiency visibility: ROCE could not be calculated, often because the company doesn't report EBIT in a standard way (common for banks).")

    debt_equity = get_latest_debt_equity(company_name)
    if debt_equity is not None and debt_equity > 1:
        arguments.append(f"High leverage: a debt-to-equity ratio of {round(debt_equity, 2)} means the company relies heavily on borrowed money.")

    return arguments


if __name__ == "__main__":
    case = build_bear_case("TCS")
    print(f"BEAR CASE for TCS:")
    for point in case:
        print(f"  - {point}")
