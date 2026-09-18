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


def build_bull_case(company_name):
    data = get_company_data(company_name)
    if data is None:
        return []

    arguments = []

    if data["cagr"] is not None and data["cagr"] > 10:
        arguments.append(f"Strong long-term growth: the stock has grown at {data['cagr']}% per year on average over the last 5 years.")

    if data["roe"] is not None and data["roe"] > 15:
        arguments.append(f"Efficient use of shareholder money: ROE of {data['roe']}% shows the company generates strong profit from equity.")

    if data["roce"] is not None and data["roce"] > 15:
        arguments.append(f"Efficient use of total capital: ROCE of {data['roce']}% shows strong returns on all capital employed, not just equity.")

    if data["sharpe_ratio"] is not None and data["sharpe_ratio"] > 0.5:
        arguments.append(f"Good risk-adjusted returns: a Sharpe ratio of {data['sharpe_ratio']} means the return earned was well worth the risk taken.")

    if data["net_margin"] is not None and data["net_margin"] > 15:
        arguments.append(f"Strong profitability: a net margin of {data['net_margin']}% means the company keeps a healthy share of revenue as actual profit.")

    if data["beta"] is not None and data["beta"] < 1:
        arguments.append(f"Lower volatility than the market: a beta of {data['beta']} means the stock tends to move less dramatically than the Nifty 50.")

    return arguments


if __name__ == "__main__":
    case = build_bull_case("MARUTI")
    print(f"BULL CASE for MARUTI:")
    for point in case:
        print(f"  - {point}")
