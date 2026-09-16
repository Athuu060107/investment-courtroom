import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()


def get_engine():
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    dbname = os.getenv("DB_NAME")
    return create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{dbname}")


def get_financials(company_name):
    conn = get_engine()
    query = """
        SELECT fs.period_end_date, fs.revenue, fs.ebit, fs.net_income, fs.total_debt, fs.equity
        FROM financial_statements fs
        JOIN companies c ON fs.company_id = c.company_id
        WHERE c.name = %s
        ORDER BY fs.period_end_date
    """
    df = pd.read_sql(query, conn, params=(company_name,))
    conn.dispose()
    return df


def calculate_ratios(company_name):
    df = get_financials(company_name)

    if df.empty:
        print(f"No financial data found for {company_name}")
        return None

    df["roe"] = df["net_income"] / df["equity"]
    df["roce"] = df["ebit"] / (df["equity"] + df["total_debt"])
    df["net_margin"] = df["net_income"] / df["revenue"]
    df["operating_margin"] = df["ebit"] / df["revenue"]

    result = df[["period_end_date", "roe", "roce", "net_margin", "operating_margin"]].copy()
    for col in ["roe", "roce", "net_margin", "operating_margin"]:
        result[col] = (result[col] * 100).round(2)

    return result


if __name__ == "__main__":
    result = calculate_ratios("TCS")
    print(result)
